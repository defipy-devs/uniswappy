# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2026 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
SolveDeltasRobust
─────────────────

Log-space reformulation of SolveDeltas for numerical robustness under
high-volatility price moves.

Motivation
----------
The original ``SolveDeltas`` solves a non-linear system in *linear* space
using ``scipy.optimize.fsolve``. Two behaviors make it fragile when
volatility spikes:

1. The Jacobian element ``∂F/∂u`` contains ``v/u²``, which diverges as
   either unknown approaches zero. Under a large ``Δp``, the solver's
   trajectory passes near these singularities and can return silently
   bad iterates at ``maxfev`` without raising.
2. The ``abs()`` patches in the residual introduce non-differentiability
   at zero, compounding the issue.

This class solves the *same* system reformulated in log space. Let
``U = ln|Δx|`` and ``V = ln|Δy|``. Two properties follow:

- The multiplicative price constraint ``|Δy|/|Δx| = p`` linearizes to
  ``V − U = ln p``, making one of the two equations exactly linear.
- The Jacobian's determinant at the solution scales with ``Δp`` itself,
  so larger volatility produces *better*-conditioned systems rather
  than worse ones. No ``abs()`` is needed — ``eᵁ, eⱽ > 0`` by
  construction.

A closed-form V2 seed (``u = (p·x − y) / (2p)``, ``v = p·u``) is used as
the initial guess. For V2 this seed is already the exact solution —
``fsolve`` detects a near-zero residual on the first step and returns
immediately. For V3 with virtual reserves, the seed is a close first
approximation and convergence is fast.

Backwards compatibility
-----------------------
``SolveDeltasRobust(lp).calc(p, x0, fac)`` returns signed ``(Δx, Δy)``
with the same sign convention as ``SolveDeltas.calc``:

- ``Δp ≥ 0`` (price of token0 in token1 rose): returns ``(−u, +v)``
  — the pool loses token0 and gains token1, as arbitrage removes the
  cheaper asset.
- ``Δp < 0``: returns ``(+u, −v)`` — the pool gains token0 and loses
  token1.

The ``x0`` and ``fac`` arguments are accepted for signature
compatibility. ``fac`` is passed through to ``fsolve``. ``x0`` is
ignored when a valid closed-form seed is available (i.e., whenever
``Δp != 0``); this is intentional — the closed-form seed is strictly
better than any user-supplied scalar.

Scope
-----
This class handles V2 exactly. For V3 it operates on virtual reserves
(same as the original ``SolveDeltas``), which is a correct
approximation so long as the implied swap stays within the active tick.
Tick-crossing moves are a separate problem requiring iterative tick
walking — not addressed here.
"""

import math
import warnings

from scipy.optimize import fsolve

from ...utils.data import UniswapExchangeData

warnings.filterwarnings("ignore")


# ─── Solver configuration ────────────────────────────────────────────────────
_DEFAULT_XTOL = 1e-10
_DEFAULT_MAXFEV = 100
_DEFAULT_FACTOR = 0.1
# Minimum numerator magnitude for the closed-form seed. Guards against
# log(0) when Δp is exactly representable but the closed-form numerator
# rounds to zero.
_SEED_EPS = 1e-18


class SolveDeltasRobust:

    """ Robust log-space solver for pool rebalancing swap deltas.

        Drop-in alternative to SolveDeltas with identical constructor
        signature and calc() return convention. Uses a log-transformed
        non-linear system plus an analytical Jacobian, seeded with the
        V2 closed-form solution.
    """

    def __init__(self, lp):

        """ Initialize solver state from an LP exchange.

            Parameters
            ----------
            lp : UniswapExchange or UniswapV3Exchange
                Pool to rebalance. V2 and V3 (via virtual reserves)
                supported.
        """

        self.lp = lp
        self.tkn_x = lp.factory.token_from_exchange[lp.name][lp.token0]
        self.tkn_y = lp.factory.token_from_exchange[lp.name][lp.token1]
        self.x = self._get_reserve(self.tkn_x)
        self.y = self._get_reserve(self.tkn_y)
        self.p = lp.get_price(self.tkn_x)
        self.p_prev = lp.get_price(self.tkn_x)
        self.dp = 0

    def get_lp(self):
        return self.lp

    # ─── Public API ─────────────────────────────────────────────────────────

    def calc(self, p, x0 = None, fac = None):

        """ Compute signed (Δx, Δy) that rebalances the pool to price p.

            Parameters
            ----------
            p : float
                Target price of token0 in token1 units (i.e., matches
                lp.get_price(token0)). Must be strictly positive.
            x0 : float, optional
                Present for signature compatibility with SolveDeltas;
                ignored when a valid closed-form seed is available.
            fac : float, optional
                scipy.optimize.fsolve ``factor`` parameter. Defaults
                to 0.1, matching SolveDeltas.

            Returns
            -------
            (Δx, Δy) : tuple of float
                Signed changes in the pool's (token0, token1) reserves
                required to rebalance to target price p. Sign convention
                matches SolveDeltas.calc: Δp ≥ 0 returns (−u, +v),
                Δp < 0 returns (+u, −v).

            Raises
            ------
            ValueError
                If p ≤ 0, or if the target price requires withdrawing
                more of a token than the pool contains (u ≥ x in the
                y→x direction).
        """

        if p <= 0:
            raise ValueError(
                "SolveDeltasRobust: target price must be > 0; got {}".format(p)
            )

        # Refresh state from current pool (matches SolveDeltas behavior).
        self.p = p
        self.p_prev = self.lp.get_price(self.tkn_x)
        self.dp = p - self.p_prev
        self.x = self._get_reserve(self.tkn_x)
        self.y = self._get_reserve(self.tkn_y)

        fac = _DEFAULT_FACTOR if fac is None else fac

        # Edge case: no move required. Return exactly zero rather than
        # routing to log space (where seed magnitude → 0 → ln(0) = −∞).
        if self.dp == 0:
            return 0.0, 0.0

        # Closed-form V2 seed in linear space, then transform to log.
        u_seed, v_seed = self._closed_form_seed()

        U0 = math.log(max(u_seed, _SEED_EPS))
        V0 = math.log(max(v_seed, _SEED_EPS))

        # Route to direction-specific residual + Jacobian. Both are
        # analytical; fsolve uses fprime to avoid finite-difference
        # amplification of the (already well-conditioned) Jacobian.
        if self.dp > 0:
            # Arbitrageur deposits y, withdraws x.
            residual = self._G_yx
            jacobian = self._J_yx
            sign_dx, sign_dy = -1.0, +1.0
        else:
            # Arbitrageur deposits x, withdraws y.
            residual = self._G_xy
            jacobian = self._J_xy
            sign_dx, sign_dy = +1.0, -1.0

        UV, info, ier, msg = fsolve(
            residual, [U0, V0],
            fprime = jacobian,
            xtol = _DEFAULT_XTOL,
            maxfev = _DEFAULT_MAXFEV,
            factor = fac,
            full_output = True,
        )

        if ier != 1:
            # fsolve reports non-convergence. Surface it rather than
            # silently returning a bad answer — the whole point of this
            # reformulation.
            raise RuntimeError(
                "SolveDeltasRobust: fsolve did not converge (ier={}, msg={!r}, "
                "reserves=({}, {}), p={}, dp={})".format(
                    ier, msg, self.x, self.y, self.p, self.dp
                )
            )

        # Inverse log transform: magnitudes are strictly positive.
        u = math.exp(UV[0])
        v = math.exp(UV[1])

        # Feasibility check: the y→x direction requires u < x.
        # The x→y direction has no analogous upper bound.
        if self.dp > 0 and u >= self.x:
            raise ValueError(
                "SolveDeltasRobust: target price {} requires withdrawing "
                "{} of token0 but pool only holds {}. Move is infeasible.".format(
                    self.p, u, self.x
                )
            )

        self.p_prev = p
        return sign_dx * u, sign_dy * v

    # ─── Log-space residuals and Jacobians ──────────────────────────────────

    def _G_yx(self, z):

        """ Residual for the y→x (Δp > 0) direction in log space.

            Parameters
            ----------
            z : array-like of length 2
                [U, V] = [ln|Δx|, ln|Δy|]

            Returns
            -------
            [G1, G2] : list of float
                G1: post-swap spot price residual
                G2: trade-ratio residual (linear in U, V)
        """

        U, V = z[0], z[1]
        eU = math.exp(U)
        eV = math.exp(V)

        # (x·eV + y·eU) / (x² − x·eU) − Δp
        g1 = (self.x * eV + self.y * eU) / (self.x * (self.x - eU)) - self.dp
        # V − U − ln(p)
        g2 = V - U - math.log(self.p)

        return [g1, g2]

    def _J_yx(self, z):

        """ Analytical Jacobian for _G_yx.

            ∂G1/∂U = eU · (y + eV) / (x − eU)²
            ∂G1/∂V = eV / (x − eU)
            ∂G2/∂U = −1
            ∂G2/∂V = +1
        """

        U, V = z[0], z[1]
        eU = math.exp(U)
        eV = math.exp(V)
        denom = self.x - eU

        dG1_dU = eU * (self.y + eV) / (denom * denom)
        dG1_dV = eV / denom
        return [[dG1_dU, dG1_dV], [-1.0, +1.0]]

    def _G_xy(self, z):

        """ Residual for the x→y (Δp < 0) direction in log space.

            The denominator is x² + x·eU here (reserves increase in x,
            not decrease), so there is no upper-bound feasibility limit.
        """

        U, V = z[0], z[1]
        eU = math.exp(U)
        eV = math.exp(V)

        # −(x·eV + y·eU) / (x² + x·eU) − Δp
        g1 = -(self.x * eV + self.y * eU) / (self.x * (self.x + eU)) - self.dp
        g2 = V - U - math.log(self.p)

        return [g1, g2]

    def _J_xy(self, z):

        """ Analytical Jacobian for _G_xy.

            ∂G1/∂U = eU · (eV − y) / (x + eU)²
            ∂G1/∂V = −eV / (x + eU)
            ∂G2/∂U = −1
            ∂G2/∂V = +1
        """

        U, V = z[0], z[1]
        eU = math.exp(U)
        eV = math.exp(V)
        denom = self.x + eU

        dG1_dU = eU * (eV - self.y) / (denom * denom)
        dG1_dV = -eV / denom
        return [[dG1_dU, dG1_dV], [-1.0, +1.0]]

    # ─── Private helpers ────────────────────────────────────────────────────

    def _closed_form_seed(self):

        """ V2 closed-form magnitudes as the initial guess.

            In log space the system collapses to a 1D equation whose
            V2 solution is:
              u = |p·x − y| / (2p)
              v = p · u

            For V2 this is the exact answer. For V3 on virtual
            reserves it is a close first approximation.
        """

        numerator = abs(self.p * self.x - self.y)
        u = numerator / (2.0 * self.p)
        v = self.p * u
        return u, v

    def _get_reserve(self, tkn):

        """ V2/V3 dispatch for reserve access.

            Mirrors SolveDeltas._get_reserve so the two classes share
            the same state-read semantics.
        """

        if self.lp.version == UniswapExchangeData.VERSION_V2:
            return self.lp.get_reserve(tkn)
        elif self.lp.version == UniswapExchangeData.VERSION_V3:
            return self.lp.get_virtual_reserve(tkn)
