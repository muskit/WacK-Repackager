def song_id_from_int(num: int):
    if num < 0:
        raise ValueError("cannot be negative")

    if num <= 999:
        return f"S00-{str(num).zfill(3)}"

    s = int(num / 1000)
    return f"S{str(s).zfill(2)}-{str(num - 1000*s).zfill(3)}"


def awb_index(id: str):
    tokens = id.split("_")
    if len(tokens) < 2:
        return None
    return (tokens[0], int(tokens[1]))
