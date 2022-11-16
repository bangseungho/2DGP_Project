from pico2d import *
from enemy import *
from enum import Enum
import random
import game_framework
import game_world


class RUN:
    @staticmethod
    def enter(self, event):
        if self.dir == 0:
            self.dir = 1
        self.timer = -1
        self.set_speed(1.3, 4)
        self.set_image(24, 19, 0)
        pass

    @staticmethod
    def exit(self, event):
        pass

    @staticmethod
    def do(self):
        self.face_dir = self.dir
        self.frame = (self.frame + self.FRAMES_PER_ACTION *
                      self.ACTION_PER_TIME * game_framework.frame_time) % self.FRAMES_PER_ACTION

        self.y -= self.RUN_SPEED_PPS * game_framework.frame_time * 1.5
        if self.y < 90:
            self.y = 90

        if self.dis_to_player <= 100 and self.y > play_state.player.y:
            if self.x < play_state.player.screen_x:
                self.dir = 1
            else:
                self.dir = -1
        
        if self.dis_to_player <= 60 and self.cooltime == 0:
            self.add_event(PATROL)

        self.x += self.dir * self.RUN_SPEED_PPS * game_framework.frame_time



        self.timer -= 1
        
        if self.cooltime > 0:
            self.cooltime -= 1
        
        if self.timer == 0:
            self.add_event(TIMER)
        

    def draw(self):
        self.scomposite_draw()

class JUMP:
    @staticmethod
    def enter(self, event):
        self.set_speed(1.5, 2)
        self.temp_dir = 1
        pass

    @staticmethod
    def exit(self, event):
        pass

    @staticmethod
    def do(self):
        self.face_dir = self.dir
        self.frame = (self.frame + self.FRAMES_PER_ACTION *
                      self.ACTION_PER_TIME * game_framework.frame_time) % self.FRAMES_PER_ACTION


        self.x += self.dir * self.RUN_SPEED_PPS * game_framework.frame_time * 1.3

        if self.y > 160:
            self.temp_dir *= -1
        
        if self.y < 90:
            self.y = 90
            self.add_event(TURN)
            
        self.y += self.temp_dir * self.RUN_SPEED_PPS * game_framework.frame_time * 1.5


    def draw(self):
        self.scomposite_draw()


class ATTACK:
    @staticmethod
    def enter(self, event):
        self.frame = 0
        self.set_speed(1.3, 15)
        self.set_image(64, 64, 38)
        pass

    @staticmethod
    def exit(self, event):
        self.cooltime = 1000
        pass

    @staticmethod
    def do(self):
        self.face_dir = self.dir
        self.frame = (self.frame + self.FRAMES_PER_ACTION *
                      self.ACTION_PER_TIME * game_framework.frame_time)
        
        if int(self.frame) == 15:
            self.add_event(TURN)

    def draw(self):
        self.scomposite_draw()


class DEATH:
    cnt = 0
    @staticmethod
    def enter(self, event):
        self.frame = 0
        self.set_speed(1.3, 2)
        self.set_image(24, 18, 166)
        pass

    @staticmethod
    def exit(self, event):
        pass

    @staticmethod
    def do(self):
        self.face_dir = self.dir_damge

        self.x += self.dir_damge / 10

        self.death_timer -= 1

        if self.death_timer == 0:
            self.x = -10000
            game_world.remove_object(self)

    def draw(self):
        DEATH.cnt += 1

        if self.death_timer > 500:
            self.scomposite_draw()
        elif DEATH.cnt % 2 == 0:
            self.scomposite_draw()


class Spark(Enemy):
    image = None

    def __init__(self):
        super(Spark, self).__init__(random.randint(800, 1000), 90, 24, 19, 0, RUN)
        if Spark.image == None:
            Spark.image = load_image("resource/spark.png")
        self.temp_dir = 1
        self.next_state = {
            RUN:  { TIMER: JUMP, PATROL: ATTACK, DAMAGED: DEATH },
            JUMP: { TURN: RUN, PATROL: ATTACK, DAMAGED: DEATH },
            ATTACK: { TURN: RUN, DAMAGED: DEATH },
            DEATH : { TURN: DEATH, PATROL: DEATH, DAMAGED: DEATH }

        }

    def scomposite_draw(self):
        if self.face_dir == 1:
            self.image.clip_composite_draw(int(
                self.frame) * self.w, self.image_posY, self.w, self.h, 0, ' ', self.x, self.y, self.w * 2, self.h * 2)
        else:
            self.image.clip_composite_draw(int(
                self.frame) * self.w, self.image_posY, self.w, self.h, 0, 'h', self.x, self.y, self.w * 2, self.h * 2)

    def handle_collision(self, other, group):
        if group == 'enemy:ob':
            self.dir *= -1
            self.timer = random.randint(200, 600)
        if group == 'star:enemy':
            self.add_event(DAMAGED)
            self.dir_damge = other.face_dir
