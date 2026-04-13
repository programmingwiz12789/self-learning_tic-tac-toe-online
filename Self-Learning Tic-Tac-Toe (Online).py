from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import random

def Win(board, player):
    d1Cnt = 0
    d2Cnt = 0
    for i in range(BOARD_SIZE):
        rowCnt = 0
        colCnt = 0
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                rowCnt += 1
            if board[j][i] == player:
                colCnt += 1
        if rowCnt == BOARD_SIZE or colCnt == BOARD_SIZE:
            return True
    for i in range(BOARD_SIZE):
        if board[i][i] == player:
            d1Cnt += 1
        if board[i][BOARD_SIZE - 1 - i] == player:
            d2Cnt += 1
    if d1Cnt == BOARD_SIZE or d2Cnt == BOARD_SIZE:
        return True
    return False

def Draw(board):
    if not Win(board, PIECE) and not Win(board, 3 - PIECE):
        empties = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == 0:
                    empties += 1
        return empties == 0
    return False

def Reward(board):
    if Win(board, PIECE):
        return WIN_SCORE
    elif Win(board, 3 - PIECE):
        return LOSS_SCORE
    elif Draw(board):
        return DRAW_SCORE
    else:
        aiWins = 0
        aiD1Bool = True
        aiD2Bool = True
        oppWins = 0
        oppD1Bool = True
        oppD2Bool = True
        for i in range(BOARD_SIZE):
            aiRowBool = True
            aiColBool = True
            oppRowBool = True
            oppColBool = True
            for j in range(BOARD_SIZE):
                if board[i][j] == 3 - PIECE:
                    aiRowBool = False
                elif board[i][j] == PIECE:
                    oppRowBool = False
                if board[j][i] == 3 - PIECE:
                    aiColBool = False
                elif board[j][i] == PIECE:
                    oppColBool = False
            if aiRowBool:
                aiWins += 1
            if aiColBool:
                aiWins += 1
            if oppRowBool:
                oppWins += 1
            if oppColBool:
                oppWins += 1
        for i in range(BOARD_SIZE):
            if board[i][i] == 3 - PIECE:
                aiD1Bool = False
            elif board[i][i] == PIECE:
                oppD1Bool = False
            if board[i][BOARD_SIZE - 1 - i] == 3 - PIECE:
                aiD2Bool = False
            elif board[i][BOARD_SIZE - 1 - i] == PIECE:
                oppD2Bool = False
        if aiD1Bool:
            aiWins += 1
        if aiD2Bool:
            aiWins += 1
        if oppD1Bool:
            oppWins += 1
        if oppD2Bool:
            oppWins += 1
        return aiWins - oppWins

def GetState(board):
    value = 0
    base = 1
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            value += base * board[i][j]
            base *= 3
    return value

def Action(Q, state, actions):
    action = -1
    if random.uniform(0, 1) < epsilon:
        action = actions.index(RandomMove(board, actions))
    else:
        max_q = -INF
        for a in range(len(Q[state])):
            if board[actions[a][0]][actions[a][1]] == 0:
                if Q[state][a] > max_q:
                    max_q = Q[state][a]
                    action = a
    return action

def RandomMove(board, actions):
    legalActions = []
    for action in actions:
        if board[action[0]][action[1]] == 0:
            legalActions.append(action)
    index = random.randint(0, len(legalActions) - 1)
    move = legalActions[index]
    return move

def AIMove(actions, cells):
    global board, state, nextState, action
    state = GetState(board)
    action = Action(Q, state, actions)
    row, col = actions[action]
    board[row][col] = PIECE
    reward = Reward(board)
    nextState = GetState(board)
    Q[state][action] += alpha * (reward + gamma * max(Q[nextState]) - Q[state][action])
    index = row * BOARD_SIZE + col
    cells[index].click()

def Wait(driver):
    global board
    oppMoved = False
    while not oppMoved:
        cells = driver.find_elements(By.CLASS_NAME, "cell")
        k = 0
        while k < len(cells) and not oppMoved:
            r, c = k // BOARD_SIZE, k % BOARD_SIZE
            piece = cells[k].text
            p = 0
            if piece == 'X':
                p = 1
            elif piece == 'O':
                p = 2
            k += 1
            if board[r][c] != p:
                board[r][c] = 3 - PIECE
                oppMoved = True

def UpdateQTable(state, nextState, action, reward):
    Q[state][action] += alpha * (reward + gamma * max(Q[nextState]) - Q[state][action])

def Reset(stateSpace, driver):
    global board, epsilon
    board = []
    for _ in range(BOARD_SIZE):
        temp = []
        for __ in range(BOARD_SIZE):
            temp.append(0)
        board.append(temp)
    epsilon -= 1 / stateSpace
    WebDriverWait(driver=driver, timeout=10).until(EC.visibility_of_element_located((By.ID, "reload")))
    driver.find_element(By.ID, "reload").click()
    filled = BOARD_SIZE * BOARD_SIZE
    while filled > 0:
        filled = 0
        cells = driver.find_elements(By.CLASS_NAME, "cell")
        for cell in cells:
            if cell.text is None:
                filled += 1

BOARD_SIZE = 3
PIECE = 1
INF = 1e9
WIN_SCORE = 1000
LOSS_SCORE = -1000
DRAW_SCORE = 0

board = []
k = 0

epsilon = 0.9
alpha = 0.01
gamma = 0.6
state = -1
nextState = -1
action = -1
actions = []
stateSpace = 3 ** (BOARD_SIZE ** 2)
Q = []

driver = webdriver.Chrome()

driver.get("https://tictactoefree.com")

for i in range(BOARD_SIZE):
    row = [0] * BOARD_SIZE
    board.append(row)

cells = driver.find_elements(By.CLASS_NAME, "cell")

for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
        actions.append((i, j))

actionSpace = len(actions)

for s in range(stateSpace):
    temp = []
    for a in range(actionSpace):
        temp.append(0)
    Q.append(temp)

while driver.find_element(By.ID, "handlerDiff").text != "HARD":
    driver.find_element(By.ID, "handlerDiff").click()

startsFirst = True
turn = startsFirst

while True:
    if turn:
        AIMove(actions, cells)
    else:
        Wait(driver)
    turn = not turn
    if Win(board, PIECE):
        Reset(stateSpace, driver)
        startsFirst = not startsFirst
        turn = startsFirst
    elif Win(board, 3 - PIECE):
        UpdateQTable(state, nextState, action, LOSS_SCORE)
        Reset(stateSpace, driver)
        startsFirst = not startsFirst
        turn = startsFirst
    elif Draw(board):
        UpdateQTable(state, nextState, action, DRAW_SCORE)
        Reset(stateSpace, driver)
        startsFirst = not startsFirst
        turn = startsFirst
