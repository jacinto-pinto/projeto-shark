import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import Counter

SUMMONER_NAME = "hitwp1"
REGION = "euw"

def get_opgg_html(summoner_name, region):
    url = f"https://www.op.gg/summoners/{region}/{summoner_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def parse_opgg_data(html):
    soup = BeautifulSoup(html, "html.parser")
    # Winrate e partidas
    try:
        summary = soup.find("div", class_="css-1v4eu7x e1oulx2j1").text
        # Exemplo: "13G 7W 6L"
        total_games = int(summary.split("G")[0])
        wins = int(summary.split(" ")[1][:-1])
        losses = int(summary.split(" ")[2][:-1])
        win_rate = int((wins / total_games) * 100)
    except Exception:
        total_games = wins = losses = win_rate = 0

    # KDA geral
    try:
        kda_block = soup.find("div", class_="css-1v4eu7x e1oulx2j2").text
        # Exemplo: "8.5 / 8.5 / 18.5"
        kda_parts = kda_block.split("/")
        avg_kills = float(kda_parts[0].strip())
        avg_deaths = float(kda_parts[1].strip())
        avg_assists = float(kda_parts[2].strip())
    except Exception:
        avg_kills = avg_deaths = avg_assists = 0

    # Campeões mais jogados
    champ_counter = Counter()
    champ_kda = {}
    champ_wr = {}
    try:
        champ_rows = soup.select("div.css-1v4eu7x.e1oulx2j4 div.css-1v4eu7x.e1oulx2j5")
        for row in champ_rows:
            champ_name = row.find("div", class_="css-1v4eu7x e1oulx2j6").text.strip()
            wr = row.find("div", class_="css-1v4eu7x e1oulx2j7").text.strip()
            kda = row.find("div", class_="css-1v4eu7x e1oulx2j8").text.strip()
            champ_counter[champ_name] += 1
            champ_kda[champ_name] = kda
            champ_wr[champ_name] = wr
    except Exception:
        pass

    # Histórico de partidas (apenas nomes dos campeões)
    matches = []
    try:
        match_blocks = soup.select("div.css-1v4eu7x.e1oulx2j9")
        for block in match_blocks[:10]:
            champ = block.find("img")["alt"]
            result = "Vitória" if "win" in block["class"] else "Derrota"
            matches.append((champ, result))
    except Exception:
        pass

    return {
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_kills": avg_kills,
        "avg_deaths": avg_deaths,
        "avg_assists": avg_assists,
        "champ_counter": champ_counter,
        "champ_kda": champ_kda,
        "champ_wr": champ_wr,
        "matches": matches
    }

def plot_opgg_stats(data):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.5, 1, 0.5, 2])

    # 1. Informações Gerais
    ax_info = fig.add_subplot(gs[0, 0])
    ax_info.text(0.1, 0.5, f"{data['total_games']}G {data['wins']}W {data['losses']}L", fontsize=14, color='white')
    ax_info.axis('off')
    kda_text = f"{data['avg_kills']:.1f} / {data['avg_deaths']:.1f} / {data['avg_assists']:.1f}"
    ax_info.text(0.5, 0.5, kda_text, fontsize=12, color='white')

    # 2. Campeões mais jogados
    ax_champs = fig.add_subplot(gs[0, 1])
    y_pos = 0.8
    for champ, _ in data['champ_counter'].most_common(3):
        wr = data['champ_wr'].get(champ, "0%")
        kda = data['champ_kda'].get(champ, "0:1 KDA")
        ax_champs.text(0.1, y_pos, f"{champ}", fontsize=10, color='white')
        ax_champs.text(0.4, y_pos, f"{wr}", fontsize=10, color=('#1f87e0' if wr != "0%" else '#e84057'))
        ax_champs.text(0.6, y_pos, f"{kda}", fontsize=10, color='gray')
        y_pos -= 0.3
    ax_champs.axis('off')

    # 3. Taxa de Vitória
    ax_wr = fig.add_subplot(gs[1, 0])
    win_rate = data['win_rate']
    wedges, texts, autotexts = ax_wr.pie([win_rate, 100-win_rate], colors=['#1f87e0', '#e84057'], startangle=90, labels=['Vitórias', 'Derrotas'], autopct='%d%%')
    ax_wr.text(0, 0, f"{win_rate}%", ha='center', va='center', fontsize=20, color='white')

    # 4. Histórico de Partidas
    ax_matches = fig.add_subplot(gs[3, :])
    cell_text = []
    cell_colors = []
    for champ, result in data['matches']:
        cell_text.append([
            champ,
            result
        ])
        color = '#1f87e0' if result == "Vitória" else '#e84057'
        cell_colors.append([color]*2)
    table = ax_matches.table(cellText=cell_text,
                             colLabels=['Campeão', 'Resultado'],
                             loc='center',
                             cellColours=cell_colors,
                             cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 2)
    for k, cell in table._cells.items():
        cell.set_text_props(color='white')
        cell.set_edgecolor('#1a1a1a')
        if k[0] == 0:
            cell.set_facecolor('#1a1a1a')
            cell.set_text_props(weight='bold')
    ax_matches.axis('off')

    fig.patch.set_facecolor('#0a0a0a')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    html = get_opgg_html(SUMMONER_NAME, REGION)
    data = parse_opgg_data(html)
    plot_opgg_stats(data)