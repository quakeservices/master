# ProtocolResponse schema

- [1. [Required] Property `ProtocolResponse > game`](#game)
- [2. [Optional] Property `ProtocolResponse > active`](#active)
- [3. [Required] Property `ProtocolResponse > request_type`](#request_type)
- [4. [Required] Property `ProtocolResponse > response_class`](#response_class)
- [5. [Optional] Property `ProtocolResponse > response`](#response)
- [6. [Optional] Property `ProtocolResponse > players`](#players)
  - [6.1. ProtocolResponse > players > players items](#autogenerated_heading_2)
    - [6.1.1. Property `ProtocolResponse > players > players items > additionalProperties`](#players_items_additionalProperties)
- [7. [Optional] Property `ProtocolResponse > details`](#details)
  - [7.1. [Optional] Property `ProtocolResponse > details > additionalProperties`](#details_additionalProperties)
    - [7.1.1. Property `ProtocolResponse > details > additionalProperties > anyOf > item 0`](#details_additionalProperties_anyOf_i0)
    - [7.1.2. Property `ProtocolResponse > details > additionalProperties > anyOf > item 1`](#details_additionalProperties_anyOf_i1)

**Title:** ProtocolResponse schema

| Type                      | `object`                                                                  |
| ------------------------- | ------------------------------------------------------------------------- |
| **Additional properties** | [[Any type: allowed]](# "Additional Properties of any type are allowed.") |
| **Defined in**            | #/definitions/ProtocolResponse                                            |

| Property                             | Pattern | Type             | Deprecated | Definition | Title/Description |
| ------------------------------------ | ------- | ---------------- | ---------- | ---------- | ----------------- |
| + [game](#game )                     | No      | string           | No         | -          | Game              |
| - [active](#active )                 | No      | boolean          | No         | -          | Active            |
| + [request_type](#request_type )     | No      | enum (of string) | No         | -          | Request Type      |
| + [response_class](#response_class ) | No      | enum (of string) | No         | -          | Response Class    |
| - [response](#response )             | No      | string           | No         | -          | Response          |
| - [players](#players )               | No      | array of object  | No         | -          | Players           |
| - [details](#details )               | No      | object           | No         | -          | Details           |

## <a name="game"></a>1. [Required] Property `ProtocolResponse > game`

**Title:** Game

| Type | `string` |
| ---- | -------- |

**Description:** Name of the game

## <a name="active"></a>2. [Optional] Property `ProtocolResponse > active`

**Title:** Active

| Type        | `boolean` |
| ----------- | --------- |
| **Default** | `true`    |

**Description:** False in the event of a server sending a 'shutdown' requestTrue all other times

## <a name="request_type"></a>3. [Required] Property `ProtocolResponse > request_type`

**Title:** Request Type

| Type | `enum (of string)` |
| ---- | ------------------ |

**Description:** Type of request

Must be one of:
* "client"
* "server"
* "any"

## <a name="response_class"></a>4. [Required] Property `ProtocolResponse > response_class`

**Title:** Response Class

| Type | `enum (of string)` |
| ---- | ------------------ |

**Description:** Response class

Must be one of:
* "ping"
* "heartbeat"
* "shutdown"
* "query"

## <a name="response"></a>5. [Optional] Property `ProtocolResponse > response`

**Title:** Response

| Type       | `string` |
| ---------- | -------- |
| **Format** | `binary` |

**Description:** Response header

## <a name="players"></a>6. [Optional] Property `ProtocolResponse > players`

**Title:** Players

| Type | `array of object` |
| ---- | ----------------- |

**Description:** List of server players if response belongs to a server

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [players items](#players_items) | -           |

### <a name="autogenerated_heading_2"></a>6.1. ProtocolResponse > players > players items

| Type                      | `object`                                                                                                                |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Additional properties** | [[Should-conform]](#players_items_additionalProperties "Each additional property must conform to the following schema") |

| Property                                                       | Pattern | Type   | Deprecated | Definition | Title/Description |
| -------------------------------------------------------------- | ------- | ------ | ---------- | ---------- | ----------------- |
| - [additionalProperties](#players_items_additionalProperties ) | No      | string | No         | -          | -                 |

#### <a name="players_items_additionalProperties"></a>6.1.1. Property `ProtocolResponse > players > players items > additionalProperties`

| Type | `string` |
| ---- | -------- |

## <a name="details"></a>7. [Optional] Property `ProtocolResponse > details`

**Title:** Details

| Type                      | `object`                                                                                                          |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Additional properties** | [[Should-conform]](#details_additionalProperties "Each additional property must conform to the following schema") |

**Description:** Server details if response belongs to a server

| Property                                                 | Pattern | Type        | Deprecated | Definition | Title/Description |
| -------------------------------------------------------- | ------- | ----------- | ---------- | ---------- | ----------------- |
| - [additionalProperties](#details_additionalProperties ) | No      | Combination | No         | -          | -                 |

### <a name="details_additionalProperties"></a>7.1. [Optional] Property `ProtocolResponse > details > additionalProperties`

| Type                      | `combining`                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| **Additional properties** | [[Any type: allowed]](# "Additional Properties of any type are allowed.") |

| Any of(Option)                                   |
| ------------------------------------------------ |
| [item 0](#details_additionalProperties_anyOf_i0) |
| [item 1](#details_additionalProperties_anyOf_i1) |

#### <a name="details_additionalProperties_anyOf_i0"></a>7.1.1. Property `ProtocolResponse > details > additionalProperties > anyOf > item 0`

| Type | `string` |
| ---- | -------- |

#### <a name="details_additionalProperties_anyOf_i1"></a>7.1.2. Property `ProtocolResponse > details > additionalProperties > anyOf > item 1`

| Type | `integer` |
| ---- | --------- |

----------------------------------------------------------------------------------------------------------------------------
Generated using [json-schema-for-humans](https://github.com/coveooss/json-schema-for-humans) on 2022-07-31 at 11:50:03 +1000