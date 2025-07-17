import pygame # type: ignore
import sys
import copy

gameRows = 15
gameCols = 15
cellSize = 45

width = gameRows * cellSize # width of the grid
height = gameCols * cellSize # height of the window
windowWidth = width + 200 # width of the whole window
cellCenter = cellSize // 2

blackLine = (0, 0, 0)
backgroundColor = (245, 222, 179)
player_color = (0, 0, 0)
AI_player = (255, 255, 255)

isMenu=True # check if the menu which is open or not
easy_mode = False  # Toggle for easy mode

depth=0 # Choose the depth depend on the difficulty


pygame.font.init()
font = pygame.font.SysFont("Arial", 24)

def startMenu(window):
    

    easyX,easyY=windowWidth//2-60,height//2
    mediumY=height//2+60
    hardY=height//2+120
    window.fill(backgroundColor)
    difficultyText=font.render("Animus Gomoko Game",True,(0,0,0))
    window.blit(difficultyText,(windowWidth//3+40,height//4-50))
    difficultyText=font.render("Choose your difficulty",True,(100,100,100))
    window.blit(difficultyText,(windowWidth//3+40,height//3+5))
    pygame.draw.rect(window,(255,255,255),(windowWidth//2-60,height//2,120,50),0)
    easyText=font.render("Easy",True,(0,10,250))
    window.blit(easyText,(windowWidth//2-30,height//2+5))

    pygame.draw.rect(window,(255,255,255),(windowWidth//2-60,height//2+60,120,50),0)
    easyText=font.render("Medieum",True,(0,10,250))
    window.blit(easyText,(windowWidth//2-45,height//2+65))

    pygame.draw.rect(window,(255,255,255),(windowWidth//2-60,height//2+120,120,50),0)
    easyText=font.render("Hard",True,(0,10,250))
    window.blit(easyText,(windowWidth//2-30,height//2+125))

    logo=pygame.image.load("gameLogo.png")
    logo= pygame.transform.scale(logo, (100,100))
    window.blit(logo,(0,0))
    
    return easyX,easyY,mediumY,hardY

def drawResult(board):
    isDraw=True
    for row in range(gameRows):
        for col in range(gameCols):
            if board[row][col]!=0:
                isDraw=True
            else: 
                isDraw=False
                break
    return isDraw


def evaluate_board(board, player, easy_mode):
    if easy_mode:
        # Simple evaluation: count material difference
        score = 0
        opponent = 1 if player == 2 else 2
        for row in range(gameRows):
            for col in range(gameCols):
                if board[row][col] == player:
                    score += 1
                elif board[row][col] == opponent:
                    score -= 1
        return score
    else:
        # Complex evaluation considering consecutive stones and open ends
        score = 0
        opponent = 1 if player == 2 else 2
        directions = [(1, 0), (0, 1), (1, 1), (1, -1),(-1,1),(-1,-1)]

        for row in range(gameRows):
            for col in range(gameCols):
                if board[row][col] == 0:
                    continue

                current_player = board[row][col]
                for rowDirect, columnDirect in directions:
                    consecutive = 1
                    open_ends = 0
                    
                    # Check forward direction
                    r, c = row + rowDirect, col + columnDirect
                    while 0 <= r < gameRows and 0 <= c < gameCols and board[r][c] == current_player:
                        consecutive += 1
                        r += rowDirect
                        c += columnDirect
                    if 0 <= r < gameRows and 0 <= c < gameCols and board[r][c] == 0:
                        open_ends += 1

                    # Check backward direction
                    r, c = row - rowDirect, col - columnDirect
                    while 0 <= r < gameRows and 0 <= c < gameCols and board[r][c] == current_player:
                        consecutive += 1
                        r -= rowDirect
                        c -= columnDirect
                    if 0 <= r < gameRows and 0 <= c < gameCols and board[r][c] == 0:
                        open_ends += 1

                    # Score patterns
                    if current_player == player:
                        if consecutive >= 5:
                            score += 100000
                        else:
                            score += (10 ** consecutive) * (open_ends + 1)
                    else:
                        if consecutive >= 5:
                            score -= 100000
                        else:
                            score -= (10 ** consecutive) * (open_ends + 1)
        return score


def nextmoves(board):
    moves = set()
    for row in range(gameRows):
        for col in range(gameCols):
            if board[row][col] != 0:
                if row > 0:
                    moves.add((row-1, col)) #check the left side of the rock
                if row < gameRows - 1:
                    moves.add((row+1, col)) #check the right side of the rock
                if col > 0:
                    moves.add((row, col-1)) #check the down side of the rock
                if col < gameCols - 1:
                    moves.add((row, col+1)) #check the up side of the rock
                if col>0 and row>0:
                    moves.add((row-1, col-1)) #check the left up side of the rock
                if col<gameCols-1 and row<gameRows-1:
                    moves.add((row+1, col+1)) #check the right down side of the rock
                if col<gameCols-1 and row>0:
                    moves.add((row-1, col+1)) #check the left down side of the rock
                if col>0 and row<gameRows-1:
                    moves.add((row+1, col-1)) #check the righ up side of the rock
                
    valid_moves = [ (r, c) for (r, c) in moves if board[r][c] == 0 ]
    return valid_moves

def oneWinMove(board, turn):
    movesList = nextmoves(board)
    for move in movesList:
        row, col = move
        if board[row][col] == 0:
            new_board = [r.copy() for r in board] # create a copy from the main board to not make any change on it along the test
            new_board[row][col] = turn
            if checkWinner(new_board) == turn:
                return (row, col)
    return None

def minimax(board, max_turn, depth, alpha, beta, easy_mode):
    winner = checkWinner(board)
    if winner != 0:
        return None, 100000 if winner == 2 else -100000 #Win solution

    if depth == 0:
        return None, evaluate_board(board, 2, easy_mode) #no more depth

    possible_moves = nextmoves(board) # search about the possible moves
    if not possible_moves:
        return None, 0

    if max_turn == 2: # maximize AI player movement 
        best_score = -100000
        best_move = possible_moves[0]
        for move in possible_moves:
            new_board = [r.copy() for r in board] # create a copy from the main board
            new_board[move[0]][move[1]] = 2
            _, score = minimax(new_board, 1, depth-1, alpha, beta, easy_mode)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if not easy_mode and beta <= alpha:
                break
        return best_move, best_score
    else:
        best_score = 100000 # minimize human player movement 
        best_move = possible_moves[0]
        for move in possible_moves:
            new_board = [r.copy() for r in board] # create a copy from the main board
            new_board[move[0]][move[1]] = 1
            _, score = minimax(new_board, 2, depth-1, alpha, beta, easy_mode)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if not easy_mode and beta <= alpha:
                break
        return best_move, best_score

def AI_Player(board):
    # Check immediate win
    win_move = oneWinMove(board, 2)
    if not easy_mode and depth==4 and win_move:
        return win_move

    # Block human win
    block_move = oneWinMove(board, 1)
    if not easy_mode and depth==4 and block_move:
        return block_move

    # Strategic move with deeper search
    move, _ = minimax(board, depth, 4, -100000, 100000,easy_mode=False)  
    return move


def generateBoard(board):
    
    for i in range(gameRows):
        col_list=[]
        for j in range(gameCols):
            col_list.append(0)
        board.append(col_list)

def redrawBoard(window):
    window.fill(backgroundColor)
    
    for i in range(gameRows):
        pygame.draw.line(window,blackLine,(cellCenter,i*cellSize+cellCenter),(width-cellCenter,i*cellSize+cellCenter),1)
    for j in range (gameCols):
        pygame.draw.line(window,blackLine,(j*cellSize+cellCenter,cellCenter),(j*cellSize+cellCenter,height-cellCenter),1)

def redrawRocks(window):
    global board
    for i in range (gameRows):
        for j in range (gameCols):
            if board[i][j]==1:
                rockColor=player_color
            elif board[i][j]==2:
                rockColor=AI_player
            if board[i][j] !=0:
                pygame.draw.circle(window,rockColor,(j*cellSize+cellCenter,i*cellSize+cellCenter),cellCenter-5)


def menuButton(window):
    x=gameCols*cellSize+20
    y=250
    endX=160
    endY=40
    pygame.draw.rect(window,(250,250,250),(x,y,endX,endY),0,10)
    text= font.render("Main menu",True,(0,0,0))
    window.blit(text,(x+20,y+8))
    return x,y,endX,endY

def redrawSidePanel(window,winner):
    pygame.draw.rect(window,(220,200,200),(gameCols*cellSize,0,200,height//1.5),0)

    if winner==1:
        msg="player win"
    elif winner==2:
        msg="AI win"
    elif drawResult(board):
        msg=f"No solution , Draw !"
    elif winner==0:
        msg = f"Turn: player {'1' if turn == 1 else 'AI'}"
    

    text= font.render(msg,True,(0,0,0))
    window.blit(text,(gameCols*cellSize+20,20))

    size=f"Board: {gameRows} × {gameCols}"
    sizeText=font.render(size,True,(255,100,100))
    window.blit(sizeText,(gameCols*cellSize+20,50))
    #restart button
    x=gameCols*cellSize+20
    y=100
    endX=160
    endY=40
    pygame.draw.rect(window,(250,250,250),(x,y,endX,endY),0,10)
    restText=font.render("restart",True,(0,10,250))
    window.blit(restText,(gameCols*cellSize+70,105))
    return x,y,endX,endY

def increaseButtons(window):
    x=gameCols*cellSize+20
    y=150
    endX=50
    endY=50
    pygame.draw.rect(window,(255,255,255),(x,y,endX,endY),0,5)
    increaseSign=font.render("+",True,(0,10,250))

    window.blit(increaseSign,(x+18,y+9))
    return x,y,endX,endY

def decreaseButtons(window):
    x=gameCols*cellSize+100
    y=150
    endX=50
    endY=50
    pygame.draw.rect(window,(255,255,255),(x,y,endX,endY),0,5)
    increaseSign=font.render("-",True,(0,10,250))

    window.blit(increaseSign,(x+20,y+9))
    return x,y,endX,endY

def resize(window, change):
    global gameCols, gameRows, width, height, windowWidth
    gameCols += change
    gameRows += change
    width = gameRows * cellSize
    height = gameCols * cellSize
    windowWidth = width + 200
    
    return pygame.display.set_mode((windowWidth, height))



def getClickPostition(pos):
    x,y=pos
    col=x//cellSize
    row=y//cellSize
    return row,col


def checkAntiDiagonal(row, col, type):
    count = 1
    
    # Check down-right direction
    next_row, next_col = row + 1, col + 1
    while next_row < gameRows and next_col < gameCols and board[next_row][next_col] == type:
        count += 1
        next_row += 1
        next_col += 1

    # Check up-left direction
    prev_row, prev_col = row - 1, col - 1
    while prev_row >= 0 and prev_col >= 0 and board[prev_row][prev_col] == type:
        count += 1
        prev_row -= 1
        prev_col -= 1
    
    return 1 if count >= 5 else 0

def checkDiagonal(row, col, type):
    count = 1
    
    # Check down-left direction
    next_row, prev_col = row + 1, col - 1
    while next_row < gameRows and prev_col >= 0 and board[next_row][prev_col] == type:
        count += 1
        next_row += 1
        prev_col -= 1

    # Check up-right direction
    prev_row, next_col = row - 1, col + 1
    while prev_row >= 0 and next_col < gameCols and board[prev_row][next_col] == type:
        count += 1
        prev_row -= 1
        next_col += 1
    
    return 1 if count >= 5 else 0

def checkVertical(row, col, type):
    count = 1

    # Check downward
    next_row = row + 1
    while next_row < gameRows and board[next_row][col] == type:
        count += 1
        next_row += 1

    # Check upward
    prev_row = row - 1
    while prev_row >= 0 and board[prev_row][col] == type:
        count += 1
        prev_row -= 1
        
    return 1 if count >= 5 else 0

def checkHorizontal(row, col, type):
    count = 1
    
    # Check right
    next_col = col + 1
    while next_col < gameCols and board[row][next_col] == type:
        count += 1
        next_col += 1

    # Check left
    prev_col = col - 1
    while prev_col >= 0 and board[row][prev_col] == type:
        count += 1
        prev_col -= 1

    return 1 if count >= 5 else 0

def checkWinner(board):
    for row in range(gameRows):
        for col in range(gameCols):
            current = board[row][col]
            if current == 0:
                continue
                
            # Check all directions for current player
            if (checkVertical(row, col, current) or
                checkHorizontal(row, col, current) or
                checkDiagonal(row, col, current) or
                checkAntiDiagonal(row, col, current)):
                return current
    return 0

# game window initialization 
pygame.init()
gameWindow = pygame.display.set_mode((windowWidth, height))
pygame.display.set_caption("Animus_Gomoku")
icon = pygame.image.load("gameLogo.png")
pygame.display.set_icon(icon)
numOfFrames = pygame.time.Clock()

# main board intialization
board = []
generateBoard(board)

#set turn 
turn = 1
while True:
    if not isMenu:

        winner = checkWinner(board)
        winner=checkWinner(board)
        #reset button boundaries in the side panel
        buttonX,buttonY,limitX,LimitY=redrawSidePanel(gameWindow,winner)

        #increase button boundaries
        increaseX,increaseY,endX,endY=increaseButtons(gameWindow)

        #decrease button boundaries
        decreaseX,decreaseY,endXD,endYD=decreaseButtons(gameWindow)

        #main menu  button boundaries
        mainX,mainY,endButtonX,endButtonY=menuButton(gameWindow)

        for event in pygame.event.get():
            
            if event.type==pygame.MOUSEBUTTONDOWN and winner==0 and turn==1:
                print (checkWinner(board))
                currentRow,currentCol=getClickPostition(pygame.mouse.get_pos())
                if currentRow<gameRows and currentCol<gameCols and board[currentRow][currentCol]==0:
                    board[currentRow][currentCol]=turn
                    turn= 2 if turn==1 else 1
            elif turn == 2 and winner == 0:
                move = AI_Player(board)
                if move:
                    currentRow, currentCol = move
                    board[currentRow][currentCol] = turn
                    turn = 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if buttonX <= x < buttonX + limitX and buttonY <= y < buttonY + LimitY:
                    board.clear()
                    generateBoard(board)
                    turn = 1

                elif increaseX <= x < increaseX + endX and increaseY <= y < increaseY + endY:
                    if 5 <= gameCols <= 19 and 5 <= gameRows < 19:
                        resize(gameWindow, 1)
                        turn=1
                        board.clear()
                        generateBoard(board)

                elif decreaseX <= x < decreaseX + endXD and decreaseY <= y < decreaseY + endYD:
                    if 5 < gameCols < 19 and 5 < gameRows < 19:
                        resize(gameWindow, -1)
                        turn=1
                        board.clear()
                        generateBoard(board)
                elif mainX <= x < mainX+endButtonX and mainY<= y <mainY+endButtonY:
                    resize(gameWindow, 15-gameCols)
                    board.clear()
                    generateBoard(board)
                    turn=1
                    isMenu=1
                    

            elif event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
        redrawBoard(gameWindow)
        redrawRocks(gameWindow)
        redrawSidePanel(gameWindow,winner)
        increaseButtons(gameWindow)
        decreaseButtons(gameWindow)
        menuButton(gameWindow)
    else:
        
        xButton,easyButton,medieumButton,hardButton=startMenu(gameWindow)
        for event in pygame.event.get():
            if event.type==pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if xButton<x <xButton+120 and easyButton<y<easyButton+50:
                    easy_mode=True
                    depth=2
                    isMenu= False
                elif xButton<x<xButton+120 and medieumButton<y<medieumButton+50:
                    depth=3
                    isMenu=False
                    easy_mode=False
                elif xButton<x<xButton+120 and hardButton<y<hardButton+50:
                    easy_mode=False
                    depth=4
                    isMenu= False
                
            elif event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
   
    pygame.display.flip()
    numOfFrames.tick(60)



