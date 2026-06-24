from __future__ import annotations

from typing import Any


def run_external_asset_calculation(
    input_payload: dict[str, Any],
    parameter_payload: dict[str, Any],
    engine_version: str,
) -> dict[str, Any]:
    tax_rate = float(parameter_payload.get("default_tax_rate", 0.21))
    capital_charge_rate = float(parameter_payload.get("capital_charge_rate", 0.08))
    asset_value = float(input_payload["asset_value"])
    balance = float(input_payload["balance"])
    price = float(input_payload["price"])
    spread_bps = float(input_payload["spread_bps"])
    rate_percent = float(input_payload["rate_percent"])
    capital_allocation = float(input_payload["capital_allocation"])

    spread_income = balance * (spread_bps / 10_000)
    rate_income = balance * (rate_percent / 100)
    mark_value = balance * (price / 100)
    value_impact = mark_value - asset_value
    gross_income = spread_income + rate_income + value_impact
    tax_impact = gross_income * tax_rate
    capital_charge = capital_allocation * capital_charge_rate
    net_income = gross_income - tax_impact - capital_charge
    external_return = net_income / capital_allocation
    rotce_like_return = (net_income + capital_charge) / capital_allocation

    warnings: list[dict[str, Any]] = []
    if spread_bps > 500:
        warnings.append({"code": "HIGH_SPREAD", "message": "Spread is above the typical review threshold."})
    if price < 80 or price > 120:
        warnings.append({"code": "UNUSUAL_PRICE", "message": "Price is outside the usual review range."})
    if tax_rate <= 0:
        warnings.append({"code": "ZERO_TAX_RATE", "message": "Tax rate is zero or negative."})

    return {
        "result": {
            "external_return_percent": round(external_return * 100, 2),
            "rotce_like_return_percent": round(rotce_like_return * 100, 2),
            "gross_income": round(gross_income, 2),
            "net_income": round(net_income, 2),
            "tax_impact": round(tax_impact, 2),
            "tax_impact_percent": round((tax_impact / capital_allocation) * -100, 2),
            "projected_value": round(mark_value, 2),
            "capital_charge": round(capital_charge, 2),
            "engine_version": engine_version,
        },
        "warnings": warnings,
    }
