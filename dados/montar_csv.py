"""
Remonta o crop_yield.csv a partir do material do portal.

As quatro culturas do arquivo original compartilham exatamente as mesmas 39
medicoes climaticas — o que muda entre elas e apenas o rendimento. Guardamos os
dados nessa forma normalizada e reconstruimos o CSV no formato original.
"""
from pathlib import Path

CLIMA = """2248.92,17.72,83.4,26.01;1938.42,17.54,82.11,26.11;2301.54,17.81,82.79,26.24;2592.35,17.61,85.07,25.56;2344.72,17.61,84.12,25.76;2339.3,17.7,84.54,25.76;2326.09,18.09,84.63,26.11;2718.08,18.3,85.43,26.12;2061.61,17.8,84.36,25.88;1934.62,17.94,83.43,26.21;2217.12,18.03,84.39,26.1;2249.7,18.01,84.24,26.11;2530.96,18.15,85.33,26.02;2504.7,18.19,85.45,26.02;2686.2,18.38,85.77,26.13;2414.79,18.18,85.76,25.93;1999.53,18.2,84.36,26.27;2362.8,18.7,84.03,26.79;2792.95,18.24,86.04,25.95;2751.24,18.31,85.98,26.02;2646.28,18.4,86.02,26.1;2302.99,18.22,84.48,26.25;2692.34,18.37,85.54,26.18;2424.55,18.28,85.16,26.18;2363.63,18.35,84.92,26.28;2892.78,18.49,86.09,26.18;2729.53,18.41,86.03,26.11;3085.79,18.34,86.1,26.03;2922.18,18.43,85.51,26.23;2546.33,18.43,84.23,26.49;2938.29,18.22,85.42,26.06;2771.73,18.38,84.98,26.3;2607.96,18.37,84.67,26.35;2604.59,18.19,83.44,26.43;2308.51,18.27,83.65,26.47;2410.13,18.58,83.45,26.81;2967.41,18.67,85.48,26.46;2333.46,18.5,84.85,26.43;2109.34,18.51,83.52,26.72"""

RENDIMENTOS = {
    "Cocoa, beans": "11560,11253,9456,9321,8800,8850,9003,9880,9201,8300,5765,5812,6667,6530,6912,7138,7525,7663,8300,9274,9956,9801,7965,7919,8226,10062,12362,13056,10058,7795,10737,7979,7066,7991,11108,11487,7314,9502,8848",
    "Oil palm fruit": "169783,201436,152343,181826,178183,169781,166042,165262,183004,177543,150428,151070,172165,160862,166136,163541,164772,142425,165993,167621,168476,162240,175629,180323,184629,190626,183544,195523,182696,171189,185831,186959,181496,203399,202379,172601,199074,189657,189896",
    "Rice, paddy": "28409,27619,26041,25187,26648,26399,24686,25251,26251,27694,28178,29918,30348,30614,31619,32510,30676,28829,29415,30640,31101,32385,33596,33260,34221,33907,35277,35836,37205,36361,37468,37972,38763,29855,40223,39775,37496,37704,42550",
    "Rubber, natural": "9322,9223,9866,9718,9573,10024,10285,10010,8604,8002,6913,6546,6077,6333,6448,6562,6008,5693,5249,6484,6348,6597,7435,9139,8857,10159,9612,8599,8337,9205,9701,8865,7817,6275,6721,6248,6842,5571,5903",
}

CABECALHO = (
    "Crop,Precipitation (mm day-1),Specific Humidity at 2 Meters (g/kg),"
    "Relative Humidity at 2 Meters (%),Temperature at 2 Meters (C),Yield"
)


def montar() -> str:
    """Reproduz o arquivo original, inclusive as quebras CRLF e a ausencia de
    quebra na ultima linha."""
    clima = CLIMA.split(";")
    linhas = [CABECALHO]
    for cultura, rendimentos in RENDIMENTOS.items():
        nome = f'"{cultura}"' if "," in cultura else cultura
        for medida, rendimento in zip(clima, rendimentos.split(",")):
            linhas.append(f"{nome},{medida},{rendimento}")
    return "\r\n".join(linhas)


def hash_conferencia(texto: str) -> int:
    """Mesmo hash rolante calculado sobre o arquivo servido pelo portal."""
    h = 0
    for caractere in texto:
        h = (h * 31 + ord(caractere)) % (2**32)
    return h


if __name__ == "__main__":
    destino = Path(__file__).parent / "crop_yield.csv"
    conteudo = montar()
    destino.write_bytes(conteudo.encode("utf-8"))

    registros = conteudo.split("\r\n")[1:]
    rendimentos = [int(linha.split(",")[-1]) for linha in registros]
    print(f"{destino.name}: {len(registros)} registros, {len(conteudo)} bytes")
    print(f"hash        : {hash_conferencia(conteudo)}")
    print(f"soma Yield  : {sum(rendimentos)}")
    print(f"min/max     : {min(rendimentos)} / {max(rendimentos)}")
