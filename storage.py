def load_player_info():
    with open('player_info.txt', 'r') as file:
        read = file.readlines()
        high_score = int(read[0])
        lifetime = int(read[1])
    return high_score, lifetime

def save_player_info(high_score, lifetime):
    with open('player_info.txt', 'w') as file:
        file.write(str(int(high_score)) + '\n')
        file.write(str(int(lifetime)))