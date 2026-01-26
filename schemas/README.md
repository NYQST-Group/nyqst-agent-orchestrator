# Primitive Schemas

This directory contains formal JSON Schema definitions for the five universal primitives.

## Overview

| Schema | Purpose | Status |
|--------|---------|--------|
| [document.schema.json](document.schema.json) | Document Intelligence primitive | Draft |
| [entity.schema.json](entity.schema.json) | Entity Resolution primitive | Draft |
| [event.schema.json](event.schema.json) | Event Management primitive | Draft |
| [claim.schema.json](claim.schema.json) | Claim/Decision primitive | Draft |
| [output.schema.json](output.schema.json) | Generation/Review primitive | Draft |

## Domain Configurations

| Config | Domain | Description |
|--------|--------|-------------|
| [cre/](cre/) | Commercial Real Estate | Lease, loan, property configs |
| legal/ | Legal/Contracts | Contract, amendment, clause configs |
| insurance/ | Insurance | Policy, claim, underwriting configs |

## Usage

Schemas define the structure. Domain configurations provide:
- Extraction templates
- Event type definitions
- Claim type definitions
- Output templates
