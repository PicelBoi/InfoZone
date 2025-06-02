'''
    Copyright (C) 2025  PicelBoi

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

from .config import config
import datetime
import pygame

previous_datetime = ""
resolution = [720, 480]
intended_resolution = [720, 480]
fonts = {}

def darkorlight():
    hour = datetime.datetime.now().hour
    if hour >= 6 and hour < 20:
        return "light"
    else:
        return "dark"

def render_datetime(screen:pygame.Surface, pos, font: pygame.font.Font):
    global config, previous_datetime
    now = datetime.datetime.now()

    render = False
    current_datetime = datetime.datetime.strftime(now, "%m/%d/%Y, %H:%M:%S")

    if previous_datetime != current_datetime:
        render = True
        previous_datetime = current_datetime   
        timetext = font.render(current_datetime, True, config["color"][darkorlight()]["bottom_bar_text_color_time"])
        
        timesurf = pygame.Surface((resolution[0], timetext.get_height()))
        timesurf.fill(config["color"][darkorlight()]["bottom_bar"])
        timesurf.blit(timetext, (pos[0],0))

        screen.blit(timesurf, (0, pos[1]))

    return render

def rescale(ogsize: int, axis):
    return(resolution[axis] * (ogsize/intended_resolution[axis]))

def render_bottom_bar(bottom_bar_surface: pygame.Surface):
    bottom_bar_surface.fill(config["color"][darkorlight()]["bottom_bar"])
    bbs_rect = bottom_bar_surface.get_rect()
    bbs_rect.bottom = resolution[1]
    bbs_rect.left = 0

    return bbs_rect.topleft

def render_top_bar(top_bar_surface: pygame.Surface, logo):
    top_bar_surface.fill(config["color"][darkorlight()]["top_bar"])
    logo = pygame.transform.smoothscale(logo, (rescale(288, 0), rescale(32, 1)))
    logorect = logo.get_rect()
    logorect.centery = int(top_bar_surface.get_size()[1] / 2)
    logorect.left = int(rescale(10,0))
    top_bar_surface.blit(logo, logorect.topleft)


def render_main(screen: pygame.Surface, page):
    global fonts, config

    # Fill screen with page's background color
    screen.fill(config["color"][darkorlight()][page["bgcolor"]])
    
    # Render title
    title = fonts["bold"]["15"].render(page["title"], True, config["color"][darkorlight()]["main_text_color"])
    titlerect = title.get_rect()
    titlerect.centerx = int(screen.get_size()[0] / 2)
    titlerect.top = int(rescale(10, 1))
    screen.blit(title, titlerect.topleft)

    # Render footer
    footer = fonts["bold"]["15"].render(page["footer"], True, config["color"][darkorlight()]["main_text_color"])
    footrect = footer.get_rect()
    footrect.centerx = int(screen.get_size()[0] / 2)
    footrect.bottom = screen.get_size()[1] - int(rescale(10, 1))
    screen.blit(footer, footrect.topleft)

    # Render texts

    # Defining variables
    spacing = int(rescale(8, 1))
    main_font = fonts["normal"]["17"]

    # Height of main text surface
    main_text_line_height = main_font.get_height() + spacing
    main_text_surf_height = spacing + ((main_text_line_height) * len(page["lines"]))
    
    # make a new surface for the main dish
    main_text_surf = pygame.Surface((screen.get_size()[0], main_text_surf_height))
    main_text_rect = main_text_surf.get_rect()

    main_text_surf.fill(config["color"][darkorlight()][page["bgcolor"]])

    prev_height = spacing

    for text in page["lines"]:
        text = main_font.render(text, True, config["color"][darkorlight()]["main_text_color"])
        textrect = text.get_rect()
        if page["align"] == "center":
            textrect.centerx =  int(screen.get_size()[0]/2)
        else:
            textrect.left = rescale(10, 0)

        textrect.top = prev_height

        main_text_surf.blit(text, textrect.topleft)

        prev_height += main_text_line_height

    main_text_rect.centery = int(screen.get_size()[1] / 2)
    main_text_rect.left = 0

    screen.blit(main_text_surf, main_text_rect.topleft)

def render_lb_text(screen: pygame.Surface, text: str):
    screen.fill(config["color"][darkorlight()]["bottom_bar"])
    font = fonts["normal"]["30"]
    textsurf = font.render(text, True, config["color"][darkorlight()]["bottom_bar_text_color"])
    screen.blit(textsurf, (int(rescale(10, 0)),0))

def packettoframe(inlist, outlist):
    for packet in inlist:
        for frame in packet.decode():
            outlist.append(frame)