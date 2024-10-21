import time
import json
import requests
import difflib
from tqdm import tqdm


def fetch_nyaa(times: int) -> list:
    """
    Fetch the specified number of pages of raw nyaa data and merge together.

    :param times: Number of pages
    :return: Merged nyaa data
    """
    all_data = []
    headers = {"accept": "application/json"}
    url = "https://nyaaapi.onrender.com/nyaa?category=anime"

    for i in range(times):
        print(f"Fetched page {i + 1}")
        json = requests.get(f"{url}&page={i}", headers=headers).json()
        all_data.extend(json["data"])

    return all_data


def filter_data(data: list, min_size: float, threshold: float) -> list:
    """
    Filter data which has smaller size and smaller title.

    :param data: Merged nyaa data
    :param min_size: Minimum size in GB (recommend 1.2 to retain part of broadcasting anime)
    :param threshold: Similarity threshold (recommend 0.85)
    :return: Filtered nyaa data
    """
    print("------")

    filtered_data = []

    for item in tqdm(data, desc="Filtering data"):
        # Size filtering
        size, unit = item["size"].split()
        if unit == 'GiB' and float(size) > min_size:

            # Similarity filtering
            is_similar = False

            for filtered_item in filtered_data:
                similarity = difflib.SequenceMatcher(None, item["title"], filtered_item["title"]).ratio()
                if similarity > threshold:
                    is_similar = True
                    break

            if not is_similar:
                filtered_data.append(item)

    return filtered_data


def save_data(data: list):
    """
    Save the raw data and processed data locally.

    :param data: Filtered nyaa data
    """
    print("------")
    print("Saving data")

    title_list = []
    date = time.strftime("%Y%m%d")

    with open(f"data/raw/{date}.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    for item in data:
        title_list.append(item["title"])

    with open(f"data/processed/{date}.txt", "w") as f:
        for item in title_list:
            f.write(item + "\n")


save_data(filter_data(fetch_nyaa(20), 1.2, 0.85))
