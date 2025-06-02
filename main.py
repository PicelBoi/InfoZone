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

import pygame
from infozone import data, functions
from infozone.config import config
from infozone.functions import render_datetime, rescale, render_main, darkorlight, render_lb_text, packettoframe
import copy
import threading
import av
import numpy
import logging

logger = logging.getLogger("PicelBoi InfoZone Main")

RESOLUTION = config["layout"]["resolution"]
FPS = 30000/1001
INTENDED_RESOLUTION = (720, 480)
VERSION = "1.0a"

functions.resolution = RESOLUTION
functions.intended_resolution = INTENDED_RESOLUTION

# Intro message.
print("Welcome to PicelBoi InfoZone!")
# Initialize pygame.
pygame.init()

# Initialize the window.
window = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("PicelBoi InfoZone", "InfoZone")

# Initialize fonts
fonts = {
    "normal": {
        "17":  pygame.font.Font("fonts/KurintoMonoNormal.ttf", int(rescale(17, 1))),
        '30':pygame.font.Font("fonts/KurintoMonoNormal.ttf", int(rescale(30, 1)))
    },
    "bold": {
        "15": pygame.font.Font("fonts/KurintoMonoBold.ttf", int(rescale(15, 1))),
        "20": pygame.font.Font("fonts/KurintoMonoBold.ttf", int(rescale(20, 1)))
    }
}

functions.fonts = fonts

# Options.

alert = False

# Grab data.
data.dataSetUp()
data.dataGrabber()

# remember to check this
previouscolor = darkorlight()

# counters
audioframes = 0

# indexes
main_index = 0
lb_text_index =0

# The clock.
clock = pygame.time.Clock()

# Copies of pages and lines
pages = copy.deepcopy(data.pages)
lb_texts = copy.deepcopy(data.lb_line)

# Timers
main_time_elapsed = 0
data_time_elapsed = 0
lb_text_elapsed = 0

# How often should data update (in ms)
data_time_update = config["data"]["data_time_update"]

# Load images
IZLogo = pygame.image.load("images/InfoZone.svg").convert_alpha()

# Render top and bottom bars.
top_bar_surface = pygame.Surface((RESOLUTION[0], int(rescale(64, 1))))
functions.render_top_bar(top_bar_surface, IZLogo)

bottom_bar_surface = pygame.Surface((RESOLUTION[0], int(rescale(96, 1))))
bbs_topleft = functions.render_bottom_bar(bottom_bar_surface)

# Render lower bar text.
lb_text_surf = pygame.Surface((RESOLUTION[0], fonts["normal"]["30"].get_height()))
render_lb_text(lb_text_surf, lb_texts[lb_text_index])
bottom_bar_surface.blit(lb_text_surf, (0, int(rescale(35,1))))

window.blit(top_bar_surface, (0,0))
window.blit(bottom_bar_surface, bbs_topleft)

# Render main screen
main_screen = pygame.Surface((RESOLUTION[0], int(rescale(320, 1))))
render_main(main_screen, pages[main_index])

window.blit(main_screen, (0, int(rescale(64, 1))))

# Open a container and a stream.
container = av.open(config["vidoutput"]["output"], mode="w", format=config["vidoutput"]["format"])
stream = container.add_stream("h264", rate=int(FPS))
stream.width = RESOLUTION[0]
stream.height = RESOLUTION[1]
stream.pix_fmt = "yuv420p"
audstream = container.add_stream("aac", rate=48000)


inputmusic = av.open("music.mp3")
inputstream = inputmusic.streams.best("audio")

audpackets = inputmusic.demux(inputstream)

audframes = []

audioT = threading.Thread(name="Audio Thread", target=packettoframe, args=(audpackets, audframes))
audioT.run()

enabled = True

pygame.display.flip()

while enabled:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                enabled = False

        updatedisplay = False

        if main_time_elapsed > pages[main_index]["duration"]:
            main_time_elapsed = 0
            main_index += 1
            if main_index > len(pages) - 1:
                main_index = 0
                if data.grabDonePages:
                    pages = copy.deepcopy(data.pages)
                    data.grabDonePages = False
            render_main(main_screen, pages[main_index])
            window.blit(main_screen, (0, int(rescale(64, 1))))

            updatedisplay = True
        else:
            main_time_elapsed += clock.get_time()
    
        if lb_text_elapsed > config["lowerbar"]["lb_text_duration"]:
            lb_text_elapsed = 0
            lb_text_index += 1
            if lb_text_index > len(lb_texts) - 1:
                lb_text_index = 0
                if data.grabDoneLB:
                    lb_texts = copy.deepcopy(data.lb_line)
                    data.grabDoneLB = False
            render_lb_text(lb_text_surf, lb_texts[lb_text_index])
            bottom_bar_surface.blit(lb_text_surf, (0, int(rescale(35,1))))
            updatedisplay = True
        else:
            lb_text_elapsed += clock.get_time()

        if data_time_elapsed > data_time_update:
            dataT = threading.Thread(name="Data Grabber Thread", target=data.dataGrabber)
            dataT.run()
        else:
            data_time_elapsed += clock.get_time()

        if render_datetime(bottom_bar_surface, (int(rescale(10, 0)), int(rescale(10, 1))), fonts["bold"]["20"]):
            window.blit(bottom_bar_surface, bbs_topleft)
            updatedisplay = True
    
        if updatedisplay:
            pygame.display.flip()

        try:
            for packet in audstream.encode(audframes[audioframes]):
                container.mux(packet)
            audioframes += 1
        except IndexError:
            logger.info("haha, funny index error")
            pass


        frame = av.VideoFrame.from_ndarray(numpy.rot90(pygame.surfarray.array3d(window)[:,::-1]))
        for packet in stream.encode(frame):
            container.mux(packet)

        clock.tick(FPS)

    except Exception as e:
        logger.error("A critical error has been encountered while running the main loop! Exiting...")
        logger.error(e)
        enabled = False

# Flush stream
for packet in stream.encode():
    container.mux(packet)

# Close the file
container.close()

quit()