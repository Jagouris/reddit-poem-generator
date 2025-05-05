import pygame
import math
from multiprocessing import Process, Queue
from parse_comments_app import generate_poem_from_comments
import time
import requests

class Button():
    def __init__(self, surface, x, y, width, height, image, click_function, hover_image=None, clicked_image=None):
        self.parent_surface = surface
    
        #self.absolute_pos = 
    
        self.button_rect = pygame.Rect(x, y, width, height)
        
        self.click_function = click_function
        
        self.image = image
        
        if(hover_image is None):
            self.hover_image = image
        else:
            self.hover_image = hover_image
        
        if(clicked_image is None):
            self.clicked_image = image
        else:
            self.clicked_image = clicked_image
        
        self.isClicked = False
        self.isHovered = False
    
    def render(self):
        if(self.isClicked == False):
            if(self.isHovered == False):
                self.parent_surface.blit(img[self.image], self.button_rect)
            else:
                self.parent_surface.blit(img[self.hover_image], self.button_rect)
        else:
            self.parent_surface.blit(img[self.clicked_image], self.button_rect)
    
    def process(self, mouseOffsetX=0, mouseOffsetY=0):
        mousePos = pygame.mouse.get_pos()
        mouseOffset = mousePos[0]-mouseOffsetX, mousePos[1]-mouseOffsetY
        
        if(self.button_rect.collidepoint(mouseOffset)):
            self.isHovered = True
        
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                if(self.isClicked == False):
                    self.click_function()
                        
                    self.isClicked = True
            else:
                self.isClicked = False
        else:
            self.isHovered = False
            
CHUNK_SIZE = 1024
EL_API_url = "https://api.elevenlabs.io/v1/text-to-speech/5KeVioqFduwLMMmDTtmf"

def get_poem(search_term, queue):
    poem = generate_poem_from_comments(search_term)

    queue.put(poem)
    
    if(poem is not None):
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": "baecd3a46b900a1a310aa9a7b2f1cf73"
        }
        
        data = {
            "text": poem,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(EL_API_url, json=data, headers=headers)
        
        filename = "res/voiceovers/"+str(time.time())+".mp3"
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        
        queue.put(filename)
    
if __name__ == "__main__":
    pygame.init()

    screen_width = 1920
    screen_height = 1080

    screen = pygame.display.set_mode((screen_width, 1080))
    pygame.display.set_caption("Shakespeare Within")

    clock = pygame.time.Clock()

    running = True

    intro_text = pygame.font.SysFont("GothicI", 30)

    outro_text = pygame.font.SysFont("Lucida Handwriting", 50)

    search_font = pygame.font.SysFont("GothicI", 50, True)

    loading_font = pygame.font.SysFont("GothicI", 30)

    img = {
        "Shakespeare": pygame.image.load("res/shakespeare_little.png"),
        "Logo": pygame.image.load("res/Logo.png"),
        "Enter_button": pygame.image.load("res/enter_button.png"),
        "enter_clicked": pygame.image.load("res/enter_button_clicked.png"),
        "enter_hovered": pygame.image.load("res/enter_button_hovered.png"),
        "Scrollbar": pygame.image.load("res/scroll_bar2.png"),
        "Parchment": pygame.image.load("res/parchment.png"),
        "Info": pygame.image.load("res/info_text.png"),
        "create": pygame.image.load("res/create_button.png"),
        "create_hovered": pygame.image.load("res/create_button_hovered.png"),
        "trumpeter1": pygame.image.load("res/Trumpeter.png"),
        "trumpeter2": pygame.image.load("res/Trumpeter2.png"),
        "loading_element": pygame.image.load("res/loading_element.png"),
        "go_button": pygame.image.load("res/go_button.png"),
        "go_button_hovered": pygame.image.load("res/go_button_hovered.png"),
        "linebreak": pygame.image.load("res/line-break.png"),
        "finished": pygame.image.load("res/finish_button.png"),
        "finished_hovered": pygame.image.load("res/finish_button_hovered.png"),
        "listen": pygame.image.load("res/listen_button.png"),
        "listen_hovered": pygame.image.load("res/listen_button_hovered.png"),
        "linebreak2": pygame.image.load("res/line-break-2.png"),
        "try_again": pygame.image.load("res/try_again.png"),
        "try_again_hovered": pygame.image.load("res/try_again_hovered.png"),
        "try_again_text": pygame.image.load("res/try_again_text.png"),
    }

    parchment_width = 870
    parchment_height = 890

    parchment = pygame.Surface((parchment_width, parchment_height), pygame.SRCALPHA)
    
    infoRect = pygame.Rect(parchment_width/2-330, 200, 660, 300)
    infoRect_2 = pygame.Rect(parchment_width/2-330, 450, 660, 300)
    searchRect = pygame.Rect(parchment_width/2-330, 525, 660, 300)
    loadingRect = pygame.Rect(parchment_width/2-330, 325, 660, 300)
    poemRect = pygame.Rect(parchment_width/2-330, 240, 660, 600)
    titleRect = pygame.Rect(parchment_width/2-330, 125, 660, 100)
    titleRect_2 = pygame.Rect(parchment_width/2-330, 200, 660, 100)

    parchment_anim = 0
    anim_dur = 1000

    search_text = ""
    poem = None

    screen_transition = False

    anim_start = 0

    loading_thread = None

    game_state = "intro"

    next_state = "search"

    enter_button = Button(parchment, parchment_width/2-150, 675, 300, 150, "Enter_button", lambda: enter_button_function(), "enter_hovered")
    create_button = Button(parchment, parchment_width/2-250, 685, 500, 70, "create", lambda: enter_button_function(), "create_hovered")
    go_button = Button(parchment, parchment_width/2-75, 485, 149, 56, "go_button", lambda: enter_button_function(), "go_button_hovered")
    finish_button = Button(parchment, parchment_width/2+20, 730, 372, 52, "finished", lambda: enter_button_function(), "finished_hovered")
    listen_button = Button(parchment, parchment_width/2-390, 730, 372, 52, "listen", lambda: enter_button_function(), "listen_hovered")
    tryagain_button = Button(parchment, parchment_width/2-201, 550, 403, 63, "try_again", lambda: enter_button_function(), "try_again_hovered")

    bg_music = pygame.mixer.Sound("res/greensleeves_mixed.wav")
    rustle_sound = pygame.mixer.Sound("res/scroll_sound_2.wav")
    click_sound = pygame.mixer.Sound("res/click_sound.mp3")
    loaded_sound = pygame.mixer.Sound("res/finish_sound_2.wav")
    voice_audio = None

    pygame.mixer.init()
    
    bg_music.set_volume(0.8)
    click_sound.set_volume(0.6)

    bg_music.play(-1, 0, 3000)
    
    gen_output = Queue()

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if(game_state == "search" and screen_transition == False):
                if(event.type == pygame.KEYDOWN):
                    click_sound.play()
                
                    if event.key == pygame.K_BACKSPACE:
                        search_text = search_text[:-1]
                    else:
                        search_text += event.unicode

        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            if(screen_transition == False):
                if(enter_button.isClicked):
                    screen_transition = True
                
                    anim_start = pygame.time.get_ticks()
                    
                    rustle_sound.play()
                    
                    click_sound.play()
                    
                    next_state = "search"
                    
                    print(click_sound.get_volume())
                if(create_button.isClicked):
                    loading_thread = Process(target=get_poem, args=(search_text,gen_output,))
                    
                    #loading_thread = Process(target=generate_poem_from_comments, args=(search_text,poem,))
                    
                    loading_thread.start()
                    
                    screen_transition = True
                    
                    anim_start = pygame.time.get_ticks()
                    
                    temp_timer = pygame.time.get_ticks()
                    
                    rustle_sound.play()
                    
                    click_sound.play()
                    
                    next_state = "loading"
                if(go_button.isClicked):
                    screen_transition = True
                    
                    anim_start = pygame.time.get_ticks()
                    
                    rustle_sound.play()
                    
                    click_sound.play()
                    
                    bg_music.fadeout(3000)
                    
                    print(poem)
                    
                    next_state = "poem"
                if(finish_button.isClicked):
                    screen_transition = True
                    
                    anim_start = pygame.time.get_ticks()
                    
                    rustle_sound.play()
                    
                    click_sound.play()
                    
                    voice_audio.fadeout(3000)
                    
                    bg_music.play(-1, 0, 3000)
                    print("finish")
                  
                    next_state = "intro"
                if(tryagain_button.isClicked):
                    screen_transition = True
                    
                    anim_start = pygame.time.get_ticks()
                    
                    rustle_sound.play()
                    
                    click_sound.play()
                    
                    search_text = ""
                    
                    next_state = "search"
                if(listen_button.isClicked):
                    voice_audio.stop()
                
                    voice_audio.play()
        
        if(game_state == "loading" and not loading_thread.is_alive() and screen_transition == False):    
            poem = gen_output.get()
            
            print(poem)
            
            if(poem is None):
                loading_thread.join()
            
                screen_transition = True
                
                anim_start = pygame.time.get_ticks()
                    
                rustle_sound.play()
                    
                next_state = "tryagain"
            else:
                voice_audio = pygame.mixer.Sound(gen_output.get())
                
                print(poem)
                
                loading_thread.join()
                
                loaded_sound.play()
                
                game_state = "ready"
        
        screen.fill("black")
        
        if(screen_transition):
            parchment_anim = (math.sin((pygame.time.get_ticks()-anim_start)/anim_dur-math.pi/2)*185+185)
            
            if((pygame.time.get_ticks()-anim_start)/anim_dur > math.pi):
                if(next_state == "intro"):
                    search_text = ""
                    
                    poem = None
                    
                    voice_audio = None
            
                if(next_state == "poem" and voice_audio.get_num_channels() == 0):
                    voice_audio.play(0, 0, 0)
            
                game_state = next_state
            
            if((pygame.time.get_ticks()-anim_start)/anim_dur > math.pi*2):
                screen_transition = False
                
                parchment_anim = 0

        parchment.fill((0, 0, 0, 0))
        
        parchment.blit(img["Parchment"], (0, 0))
        
        if(game_state == "intro"):
            parchment.blit(img["Shakespeare"], (parchment_width/2-111, 380))
            parchment.blit(img["Logo"], (parchment_width/2-330, 125))
            #parchment.blit(img["Enter_button"], (parchment_width/2-90, 685))
            parchment.blit(img["trumpeter1"], (100, 555))
            parchment.blit(img["trumpeter2"], (600, 555))
            enter_button.process(screen_width/2-435, 95)
            enter_button.render()
        elif(game_state == "search"):
            parchment.blit(img["Info"], (parchment_width/2-350, 150))
            create_button.process(screen_width/2-435, 95)
            create_button.render()
            
            drawText(parchment, search_text, "black", searchRect, search_font, 2, True, None)
        elif(game_state == "loading"):
            drawText(parchment, "Please wait...", "black", loadingRect, loading_font, 2, True, None)
            parchment.blit(img["loading_element"], (290, math.sin((pygame.time.get_ticks())/200)*10+400))
        elif(game_state == "ready"):
            drawText(parchment, "Your poem is complete! Click Go when you're ready.", "black", loadingRect, loading_font, 2, True, None)
            
            go_button.process(screen_width/2-435, 95)
            go_button.render()
        elif(game_state == "poem"):
            drawText(parchment, "A poem about "+search_text, "black", titleRect, loading_font, 2, True, None)
            
            #drawText(parchment, "Donald Trump", "black", titleRect_2, search_font, 2, True, None)
            
            parchment.blit(img["linebreak"], (parchment_width/2-85, 170))
            
            drawText(parchment, poem, "black", poemRect, loading_font, 2, True, None)
            
            parchment.blit(img["linebreak2"], (parchment_width/2-8, 700))
            
            finish_button.process(screen_width/2-435, 95)
            finish_button.render()
            listen_button.process(screen_width/2-435, 95)
            listen_button.render()
        elif(game_state == "tryagain"):
            parchment.blit(img["try_again_text"], (parchment_width/2-350, 250))
            
            tryagain_button.process(screen_width/2-435, 95)
            tryagain_button.render()
        
        screen.blit(parchment, (screen_width/2-435, parchment_anim+95), (0, parchment_anim, parchment_width, parchment_height-parchment_anim*2))
        
        screen.blit(img["Scrollbar"], (screen_width/2-700, parchment_anim+15))
        screen.blit(img["Scrollbar"], (screen_width/2-700, parchment_anim*-1+905))
        
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()
    
#Function written by https://stackoverflow.com/users/5577765/rabbid76
def drawText(surface, text, color, rect, font, align, aa, bkg):
    lineSpacing = -2
    spaceWidth, fontHeight = font.size(" ")[0], font.size("Tg")[1]

    listOfWords = text.split(" ")
    if bkg:
        imageList = [font.render(word, 1, color, bkg) for word in listOfWords]
        for image in imageList: image.set_colorkey(bkg)
    else:
        imageList = [font.render(word, aa, color) for word in listOfWords]

    maxLen = rect[2]
    lineLenList = [0]
    lineList = [[]]
    for image in imageList:
        width = image.get_width()
        lineLen = lineLenList[-1] + len(lineList[-1]) * spaceWidth + width
        if len(lineList[-1]) == 0 or lineLen <= maxLen:
            lineLenList[-1] += width
            lineList[-1].append(image)
        else:
            lineLenList.append(width)
            lineList.append([image])

    lineBottom = rect[1]
    lastLine = 0
    for lineLen, lineImages in zip(lineLenList, lineList):
        lineLeft = rect[0]
        if align == 1:
            lineLeft += + rect[2] - lineLen - spaceWidth * (len(lineImages)-1)
        elif align == 2:
            lineLeft += (rect[2] - lineLen - spaceWidth * (len(lineImages)-1)) // 2
        elif align == 3 and len(lineImages) > 1:
            spaceWidth = (rect[2] - lineLen) // (len(lineImages)-1)
        if lineBottom + fontHeight > rect[1] + rect[3]:
            break
        lastLine += 1
        for i, image in enumerate(lineImages):
            x, y = lineLeft + i*spaceWidth, lineBottom
            surface.blit(image, (round(x), y))
            lineLeft += image.get_width() 
        lineBottom += fontHeight + lineSpacing

    if lastLine < len(lineList):
        drawWords = sum([len(lineList[i]) for i in range(lastLine)])
        remainingText = ""
        for text in listOfWords[drawWords:]: remainingText += text + " "
        return remainingText
    return ""