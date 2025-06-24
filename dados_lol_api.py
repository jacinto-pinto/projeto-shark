import requests
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont, QColor

api_url = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/hitwp1/EUW'

api_key = "RGAPI-e9955b9e-8a28-4cf5-a478-1fe58f118812"
requests.get(api_url)

api_url = api_url + '?api_key=' + api_key
api_url
requests.get(api_url)
resp = requests.get(api_url)
player_info = resp.json()
player_info
print(player_info)

puuid = player_info['puuid']
puuid

api_url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/p39LCzQzXWVniT7BcctFfsZxuNZmf1iP6ScGQAWkQeQNmuWVePMGK2zydoK0MnBXhSPX-ORWMf3amw/ids?start=0&count=20"
#                    & instead of ?, because there's already a ? in the original
api_url = api_url + '&api_key=' + api_key 
api_url

resp = requests.get(api_url)
match_ids = resp.json()
match_ids

recent_match = match_ids[0]
recent_match
print(recent_match)

match_id = "EUW1_7441828885"
api_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"

resp = requests.get(api_url)
match_data = resp.json()

match_data

match_data.keys()

# "metadata" contains the puuid for every player in the game
match_data['metadata']

# NOTE: The order in which these puuid's appear in this the "participants" list
# is the same order they will appear for data elsewhere in this dictionary (useful for later)

# "info" contains lots of data about the game, like when it was created, how long it lasted etc...
match_data['info'].keys()

# For instance, this is how long the game lasted:
match_data['info']['gameDuration'] / 60 # / 60 to get it into minutes

# Within info, participants contains a list of length 10, each with further information about the player
len(match_data['info']['participants'])

# To save time, we'll assign a variable for first player
player_data = match_data['info']['participants'][0]
player_data

# Then, we can find out information about them in the game, like which Champion they're playing...
player_data['championName']

# Maybe their KDA?
k = player_data['kills']
d = player_data['deaths']
a = player_data['assists']
print("Kills:", k)
print("Deaths:", d)
print("Assists:", a)
print("KDA:", (k + a) / d)

# or their role?
player_data['teamPosition']

# A list of all the participants puuids
participants = match_data['metadata']['participants']
# Now, find where in the data our players puuid is found
player_index = participants.index(puuid)
player_index

# This should match the puuid we used to search for the match IDs, go back up and check
participants[player_index]

# Hopefully the name below is what you inputted into the first function!
match_data['info']['participants'][player_index]['summonerName']

player_data = match_data['info']['participants'][player_index]

champ = player_data['championName']
k = player_data['kills']
d = player_data['deaths']
a = player_data['assists']
win = player_data['win']

print("Champ:", champ, "Kills:", k, "Deaths:", d, "Assists:", a, "Win:", win)

# The first function simply gets the puuid, given a summoner name and region
# This is exactly the same as our first example, except we're building the API URL from scratch
def get_puuid(summoner_name, region, api_key):
    api_url = (
        "https://" + 
        region +
        ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" +
        summoner_name +
        "?api_key=" +
        api_key
    )
    
    print(api_url)
    
    resp = requests.get(api_url)
    player_info = resp.json()
    puuid = player_info['puuid']
    return puuid  

'''summoner_name = 'hitwp1'
region = 'euw1'

puuid = get_puuid(summoner_name, region, api_key)'''
#puuid

# The function to get a list of all the match IDs (2nd example above) given a players puuid and mass region
def get_match_ids(puuid, mass_region, api_key):
    api_url = (
        "https://" +
        mass_region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid + 
        "/ids?start=0&count=20" + 
        "&api_key=" + 
        api_key
    )
    
    print(api_url)
    
    resp = requests.get(api_url)
    match_ids = resp.json()
    return match_ids   

# NOTE: region and mass_region are different
# for instance, NA1 is the North American region
# which is part of the AMERICAS mass region
# EUW1 is Europe West region, part of the EUROPE mass region
mass_region = 'EUROPE'

match_ids = get_match_ids(puuid, mass_region, api_key)
match_ids

# From a given match ID and mass region, get the data about the game
def get_match_data(match_id, mass_region, api_key):
    api_url = (
        "https://" + 
        mass_region + 
        ".api.riotgames.com/lol/match/v5/matches/" +
        match_id + 
        "?api_key=" + 
        api_key
    )
    
    resp = requests.get(api_url)
    match_data = resp.json()
    return match_data     

match_id = match_ids[0]
match_data = get_match_data(match_id, mass_region, api_key)
match_data

# Given the match data and a players puuid, return the data about just them
def find_player_data(match_data, puuid):
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]
    return player_data

find_player_data(match_data, puuid)

# We initialise an empty dictionary to store data for each game
data = {
    'champion': [],
    'kills': [],
    'deaths': [],
    'assists': [],
    'win': []
}

for match_id in match_ids:
    print(match_id)
    
    # run the two functions to get the player data from the match ID
    match_data = get_match_data(match_id, mass_region, api_key)
    player_data = find_player_data(match_data, puuid)
    
    # assign the variables we're interested in
    champion = player_data['championName']
    k = player_data['kills']
    d = player_data['deaths']
    a = player_data['assists']
    win = player_data['win']
     
    # add them to our dataset
    data['champion'].append(champion)
    data['kills'].append(k)
    data['deaths'].append(d)
    data['assists'].append(a)
    data['win'].append(win)   

    # Data on the last 20 games of the account in question
data

# Classe da janela para mostrar os dados
class Dashboard(QWidget):
    def __init__(self, ultima_partida, historico):
        super().__init__()
        self.setWindowTitle("Histórico de Partidas - League of Legends")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        self.layout = QVBoxLayout()

        # Título para a última partida
        titulo_ultima = QLabel("Última Partida")
        titulo_ultima.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout.addWidget(titulo_ultima)

        # Mostra os dados da última partida
        campeao = ultima_partida['champion']
        kda = f"{ultima_partida['kills']} / {ultima_partida['deaths']} / {ultima_partida['assists']}"
        resultado = "Vitória" if ultima_partida['win'] else "Derrota"
        
        info_ultima = QLabel(f"Campeão: {campeao}\nKDA: {kda}\nResultado: {resultado}")
        info_ultima.setFont(QFont("Arial", 12))
        self.layout.addWidget(info_ultima)

        # Título para o histórico
        titulo_historico = QLabel("\nHistórico das Últimas 20 Partidas")
        titulo_historico.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout.addWidget(titulo_historico)

        # Cria a tabela para o histórico
        tabela = QTableWidget()
        tabela.setRowCount(len(historico['champion']))
        tabela.setColumnCount(5)
        tabela.setHorizontalHeaderLabels(['Campeão', 'Kills', 'Deaths', 'Assists', 'Resultado'])
        tabela.horizontalHeader().setStyleSheet("color: black;")
        tabela.verticalHeader().setStyleSheet("color: black;")
        
        # Preenche a tabela com os dados
        for i in range(len(historico['champion'])):
            tabela.setItem(i, 0, QTableWidgetItem(historico['champion'][i]))
            tabela.setItem(i, 1, QTableWidgetItem(str(historico['kills'][i])))
            tabela.setItem(i, 2, QTableWidgetItem(str(historico['deaths'][i])))
            tabela.setItem(i, 3, QTableWidgetItem(str(historico['assists'][i])))
            
            resultado_item = "Vitória" if historico['win'][i] else "Derrota"
            item_resultado = QTableWidgetItem(resultado_item)
            
            # Pinta a célula de azul para vitória e vermelho para derrota
            if historico['win'][i]:
                item_resultado.setForeground(QColor('#1f87e0')) # Azul
            else:
                item_resultado.setForeground(QColor('#e84057')) # Vermelho
            
            tabela.setItem(i, 4, item_resultado)

        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(tabela)
        
        self.setLayout(self.layout)

# --------------------------------------------------------------------
# Roda o programa e mostra a janela
# --------------------------------------------------------------------
if __name__ == "__main__":
    # Pega os dados da última partida (primeira da lista)
    dados_ultima_partida = {
        'champion': data['champion'][0],
        'kills': data['kills'][0],
        'deaths': data['deaths'][0],
        'assists': data['assists'][0],
        'win': data['win'][0]
    }

    # Inicia a aplicação da janela
    app = QApplication(sys.argv)
    # Cria a janela, passando os dados da última partida e o histórico
    janela = Dashboard(dados_ultima_partida, data)
    janela.resize(800, 600) # Define um tamanho inicial para a janela
    janela.show()
    sys.exit(app.exec_())
