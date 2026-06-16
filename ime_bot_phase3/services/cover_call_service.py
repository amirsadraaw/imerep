from datetime import datetime

from database.db import get_market_conn


RISK_FREE_RATE = 0.36

CONTRACT_SIZE = 1000


ETF_MAP = {

    "کهربا": "ETF_KAHRABA",

    "طلا": "ETF_TALA",

    "جواهر": "ETF_JAVAHER",

    "درخشان": "ETF_DERAKHSHAN"
}




def get_latest_price(contract_code):

    conn = get_market_conn()

    row = conn.execute("""

    SELECT last_price

    FROM snapshots

    WHERE contract_code=?

    ORDER BY rowid DESC

    LIMIT 1

    """,

    (contract_code,)

    ).fetchone()

    conn.close()

    if not row:
        return None

    return row[0]


def get_option_contracts():

    conn = get_market_conn()

    rows = conn.execute("""

    SELECT

        contract_code,

        contract_description,

        last_price,

        open_interest

    FROM snapshots

    WHERE market_type='OPTION'

    GROUP BY contract_code

    """).fetchall()

    conn.close()

    return rows


def extract_strike_price(text):

    import re

    match = re.search(r"(\d[\d,]*)\s*ریال", text)

    if not match:
        return None

    return int(

        match.group(1)

        .replace(",", "")

    )


def extract_expiry(text):

    import re

    match = re.search(
        r"(\d{4}/\d{2}/\d{2})",
        text
    )

    if not match:
        return None

    return match.group(1)


def get_days_to_expiry(persian_date):

    try:

        year, month, day = map(
            int,
            persian_date.split("/")
        )

        today = datetime.now()

        fake_gregorian = datetime(
            year - 621,
            month,
            day
        )

        delta = fake_gregorian - today

        return max(delta.days, 1)

    except:
        return 1


def calculate_covered_call():

    results = []

    option_rows = get_option_contracts()

    for row in option_rows:

        contract_code = row[0]

        description = row[1]

        option_price = row[2]

        oi = row[3]

        if not option_price:
            continue

        matched_symbol = None

        for key in ETF_MAP:

            if key in description:

                matched_symbol = ETF_MAP[key]

                break

        if not matched_symbol:
            continue

        base_price = get_latest_price(
            matched_symbol
        )

        if not base_price:
            continue

        strike_price = extract_strike_price(
            description
        )

        if not strike_price:
            continue

        expiry = extract_expiry(
            description
        )

        if not expiry:
            continue

        days = get_days_to_expiry(
            expiry
        )

        initial_capital = (

            base_price * CONTRACT_SIZE

        )

        final_value = (

            strike_price * CONTRACT_SIZE

        ) + (

            option_price * CONTRACT_SIZE

        )

        gross_profit = (

            final_value -

            initial_capital

        )

        total_return = (

            gross_profit /

            initial_capital

        ) * 100

        ytm = (

            (
                1 +

                (total_return / 100)

            ) ** (

                365 / days

            ) - 1

        ) * 100

        opportunity_cost = (

            initial_capital *

            RISK_FREE_RATE *

            (days / 365)

        )

        net_profit = (

            gross_profit -

            opportunity_cost

        )

        adjusted_return = (

            net_profit /

            initial_capital

        ) * 100

        adjusted_ytm = (

            (
                1 +

                (adjusted_return / 100)

            ) ** (

                365 / days

            ) - 1

        ) * 100

        results.append({

            "description": description,

            "expiry": expiry,

            "days": days,

            "option_price": option_price,

            "base_price": base_price,

            "initial_capital": initial_capital,

            "final_value": final_value,

            "gross_profit": gross_profit,

            "return": total_return,

            "ytm": ytm,

            "opportunity_cost": opportunity_cost,

            "net_profit": net_profit,

            "adjusted_return": adjusted_return,

            "adjusted_ytm": adjusted_ytm,

            "oi": oi
        })

    results.sort(

        key=lambda x: x["adjusted_ytm"],

        reverse=True
    )

    return results