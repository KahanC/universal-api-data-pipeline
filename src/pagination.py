from api_client import extract_records


def fetch_all_pages(client, config):
    pagination = config.get("pagination", {})
    strategy = pagination.get("strategy", "none")

    endpoint = config.get("endpoint", "")
    params = config.get("params", {}).copy()
    record_path = config.get("record_path", "")

    if strategy not in ("none", "page", "world_bank"):
        raise ValueError(f"Unsupported pagination strategy: {strategy}")

    if strategy == "none":
        data = client.get(endpoint, params=params)
        return extract_records(data, record_path) if record_path else data

    max_pages = int(pagination.get("max_pages", 100))
    if max_pages < 1:
        raise ValueError("max_pages must be positive")

    page_param = pagination.get("page_param", "page")
    records = []

    for page in range(1, max_pages + 1):
        params[page_param] = page
        data = client.get(endpoint, params=params)

        batch = (
            extract_records(data, record_path)
            if record_path else data
        )

        if not isinstance(batch, list):
            raise ValueError("API records must be a list")

        records.extend(batch)
        print(f"Page {page}: {len(batch)} records")

        if strategy == "world_bank":
            total_pages = int(data[0]["pages"])
            if page >= total_pages:
                return records

        elif not batch:
            return records

        elif len(batch) < int(pagination.get("page_size", 100)):
            return records

    raise RuntimeError(
        f"Pagination exceeded max_pages={max_pages}; "
        "increase the limit if more pages are expected"
    )
