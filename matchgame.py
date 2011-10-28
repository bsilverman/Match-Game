#!/usr/bin/python

import sys, os, pygame, pygame.locals
from random import shuffle
 
# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)

def load_image(name):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print "Cannot load image: %s" % (name)
        raise SystemExit, message
    return image.convert()
    
class Mouse(pygame.sprite.Sprite):
    def __init__(self, size):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, size, size)
        
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        
class Card(pygame.sprite.Sprite):
     
    def __init__(self, id, face_image, back_image):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.rect = face_image.get_rect()
        self.face_image = face_image
        self.back_image = back_image
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.face_up = True
        self.flip()
    
    def place(self, x, y):
        self.rect.x = x
        self.rect.y = y
        
    def flip(self):
        if self.face_up:
            other_side_image = self.back_image
        else:
            other_side_image = self.face_image
        self.image.blit(other_side_image, (0, 0))
        self.face_up = not self.face_up
            
# Initialize Pygame
pygame.init()
 
# Set the height and width of the screen based on how many cards there are, their size,
# the space between cards, and how many columns there are
pair_count = 5
card_count = 2 * pair_count
column_count = 5
row_count = (card_count + (column_count - 1)) / column_count
card_width = 100
card_height = 200
card_spacing = 10

screen_width = (column_count * card_width) + ((column_count - 1) * card_spacing)
screen_height = (row_count * card_height) + ((row_count - 1) * card_spacing)
screen=pygame.display.set_mode([screen_width,screen_height])

# Create pairs of cards and store them in a Pygame group
back_image = load_image("card_back.bmp")
all_cards = pygame.sprite.RenderPlain()
for id in range(pair_count):
    face_image = load_image("image%d.bmp" % (id))
    all_cards.add(Card(id, face_image, back_image))
    all_cards.add(Card(id, face_image, back_image))

# Place the cards on the screen in rows and columns using a random order
row = 0
column = 0
card_list = all_cards.sprites()
shuffle(card_list)
for card in card_list:
    #print "Card %d is located in row %d, column %d" % (card.id, row, column)
    card.place(column * (card_width + card_spacing), row * (card_height + card_spacing))
    column = column + 1
    if column == column_count:
        row = row + 1
        column = 0

# Create a sprite for the mouse position so that we easily check
# to see if the mouse is over a card when clicked
mouse = Mouse(card_spacing / 2)

# Create the background, draw the cards over it, and reveal the screen
screen.fill(black)
all_cards.draw(screen)
pygame.display.flip()
 
# Record what time it is when the game started
start_time = pygame.time.get_ticks()

# -------- Main Program Loop -----------
done=False
clock=pygame.time.Clock()
selected_cards = pygame.sprite.RenderPlain()
while done == False:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True
        elif event.type == pygame.locals.MOUSEBUTTONUP:
            # Find out if there are any cards under the new mouse position
            mouse.update()
            cards_under_mouse = pygame.sprite.spritecollide(mouse, all_cards, True)
            if cards_under_mouse:
                # A card was selected, add it to our selected group, flip it over and update the display
                card = cards_under_mouse[0]
                selected_cards.add(card)
                card.flip()
                selected_cards.draw(screen)
                pygame.display.flip()
                
                # If the user has selected two cards, it's time to see if they got a match or not
                if len(selected_cards) == 2:
                    card_pair = selected_cards.sprites()
                    if card_pair[0].id == card_pair[1].id:
                        # Cards match. Don't add them back to the all_cards group since these
                        # two are no longer part of the game. Repaint the background and redraw
                        # all of the cards still in use so the two selected ones disappear.
                        screen.fill(black)
                        all_cards.draw(screen)
                    else:
                        # Cards don't match. Flip them back over, redraw them (and only them), and
                        # add them back to the all_cards group so that they will still be usable.
                        card_pair[0].flip()
                        card_pair[1].flip()
                        selected_cards.draw(screen)
                        all_cards.add(card_pair)
                    
                    # Pause a little before updating the display so that the user can see the
                    # face of both cards before we flip them back over or remove them
                    pygame.time.wait(1000)
                    pygame.display.flip()
                    
                    # Make it so that the user now has no cards selected.
                    selected_cards.empty()

    
    if len(all_cards) == 0:
        # The user found all of the cards, exit the game.
        done = True
        
        # But first tell the user how long it took to find all the matches
        game_length = pygame.time.get_ticks() - start_time
        congrats = "Congratulations! You found all the matches in %.2f seconds." % (float(game_length) / 1000)
        font = pygame.font.Font(None, 24)
        text = font.render(congrats, 1, white)
        textpos = text.get_rect()
        textpos.center = screen.get_rect().center
        screen.blit(text, textpos)
        pygame.display.flip()
        pygame.time.wait(4000)
    else:    
        # Continue playing, but pause here for a bit to limit the game to 20 frames per second
        clock.tick(20)
 
pygame.quit()
