from decimal import *
from dataclasses import dataclass

# ------------------ Constants ------------------ #

# MAX type values
MAX_UINT128 = 2**128 - 1
MAX_UINT256 = 2**256 - 1
MAX_INT256 = 2**255 - 1
MIN_INT256 = -(2**255)
MAX_UINT160 = 2**160 - 1
MIN_INT24 = -(2**24)
MAX_INT24 = 2**23 - 1
MIN_INT128 = -(2**128)
MAX_INT128 = 2**127 - 1
MAX_UINT8 = 2**8 - 1

### The minimum value that can be returned from #getSqrtRatioAtTick. Equivalent to getSqrtRatioAtTick(MIN_TICK)
MIN_SQRT_RATIO = 4295128739
### The maximum value that can be returned from #getSqrtRatioAtTick. Equivalent to getSqrtRatioAtTick(MAX_TICK)
MAX_SQRT_RATIO = 1461446703485210103287273052203988822378723970342

FixedPoint128_Q128 = 0x100000000000000000000000000000000
FixedPoint96_RESOLUTION = 96
FixedPoint96_Q96 = 0x1000000000000000000000000

ONE_IN_PIPS = 1000000

### The minimum tick that may be passed to #getSqrtRatioAtTick computed from log base 1.0001 of 2**-128
MIN_TICK = -887272
### The maximum tick that may be passed to #getSqrtRatioAtTick computed from log base 1.0001 of 2**128
MAX_TICK = -MIN_TICK


# ------------------ Shared dataclasses ------------------ #


@dataclass
class TickInfo:
    ## the total position liquidity that references this tick
    liquidityGross: int
    ## amount of net liquidity added (subtracted) when tick is crossed from left to right (right to left),
    liquidityNet: int
    ## fee growth per unit of liquidity on the _other_ side of this tick (relative to the current tick)
    ## only has relative meaning, not absolute — the value depends on when the tick is initialized
    feeGrowthOutside0X128: int
    feeGrowthOutside1X128: int


# ------------------ Shared typechecking ------------------ #


def checkUInt128(number):
    assert number >= 0 and number <= MAX_UINT128, "OF or UF of UINT128"
    assert type(number) == int, "Not an integer"


def checkInt128(number):
    assert number >= MIN_INT128 and number <= MAX_INT128, "OF or UF of INT128"
    assert type(number) == int, "Not an integer"


def checkInt256(number):
    assert number >= MIN_INT256 and number <= MAX_INT256, "OF or UF of INT256"
    assert type(number) == int, "Not an integer"


def checkUInt160(number):
    assert number >= 0 and number <= MAX_UINT160, "OF or UF of UINT160"
    assert type(number) == int, "Not an integer"


def checkUInt256(number):
    assert number >= 0 and number <= MAX_UINT256, "OF or UF of UINT256"
    assert type(number) == int, "Not an integer"


def checkUInt8(number):
    assert number >= 0 and number <= MAX_UINT8, "OF or UF of UINT8"
    assert type(number) == int, "Not an integer"


def checkInt24(number):
    assert number >= MIN_INT24 and number <= MAX_INT24, "OF or UF of INT24"
    assert type(number) == int, "Not an integer"


def checkfloat(input):
    assert type(input) == float


def checkString(input):
    assert type(input) == str


def checkDecimal(input):
    assert type(input) == Decimal


def checkDict(input):
    assert type(input) == dict


def checkAccount(address):
    checkString(address)


# Mimic unsafe overflows in Solidity
def toUint256(number):
    try:
        checkUInt256(number)
    except:
        number = number & (2**256 - 1)
        checkUInt256(number)
    return number


def toUint128(number):
    try:
        checkUInt128(number)
    except:
        number = number & (2**128 - 1)
        checkUInt128(number)
    return number


# General checkInput function for all functions that take input parameters
def checkInputTypes(**kwargs):
    if "string" in kwargs:
        loopChecking(kwargs.get("string"), checkString)
    if "decimal" in kwargs:
        loopChecking(kwargs.get("decimal"), checkDecimal)
    if "accounts" in kwargs:
        loopChecking(kwargs.get("accounts"), checkAccount)
    if "int24" in kwargs:
        loopChecking(kwargs.get("int24"), checkInt24)
    if "uint256" in kwargs:
        loopChecking(kwargs.get("uint256"), checkUInt256)
    if "int256" in kwargs:
        loopChecking(kwargs.get("int256"), checkInt256)
    if "uint160" in kwargs:
        loopChecking(kwargs.get("uint160"), checkUInt160)
    if "uint128" in kwargs:
        loopChecking(kwargs.get("uint128"), checkUInt128)
    if "int128" in kwargs:
        loopChecking(kwargs.get("int128"), checkInt128)
    if "uint8" in kwargs:
        loopChecking(kwargs.get("uint8"), checkUInt8)
    if "dict" in kwargs:
        checkDict(kwargs.get("dict"))


def loopChecking(tuple, fcn):
    try:
        iter(tuple)
    except TypeError:
        # Not iterable
        fcn(tuple)
    else:
        # Iterable
        for item in tuple:
            fcn(item)


# ------------------ Shared utility functions ------------------ #


def getHashLimit(owner, tick, isToken0):
    checkInputTypes(account=owner, int24=tick, bool=isToken0)
    return hash((owner, tick, isToken0))


def assertLimitPositionExists(self, owner, tick, isToken0):
    checkInputTypes(account=owner, int24=(tick), bool=isToken0)
    key = getHashLimit(owner, tick, isToken0)
    assert self.__contains__(key), "Position doesn't exist"
    return key


def assertLimitPositionIsBurnt(self, owner, tick, isToken0):
    checkInputTypes(account=owner, int24=(tick), bool=isToken0)
    key = getHashLimit(owner, tick, isToken0)
    assert not self.__contains__(key), "Position exists"


# Mimic Solidity uninitialized ticks in Python - inserting keys to an empty value in a map
def insertUninitializedTickstoMapping(mapping, keys):
    for key in keys:
        insertTickInMapping(mapping, key, TickInfo(0, 0, 0, 0))


def insertTickInMapping(mapping, key, value):
    assert mapping.__contains__(key) == False
    mapping[key] = value


# Insert a newly initialized tick into the dictionary.
def insertInitializedTicksToMapping(mapping, keys, ticksInfo):
    assert len(keys) == len(ticksInfo)
    for i in range(len(keys)):
        insertTickInMapping(mapping, keys[i], ticksInfo[i])
