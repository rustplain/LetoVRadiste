init python:
    import random
    import pygame

    class DragRaceMinigame(renpy.Displayable):
        def __init__(self):
            super(DragRaceMinigame, self).__init__()
            self.wins, self.losses = 0, 0
            self.reset_round()

        def reset_round(self):
            self.player_x, self.sanya_x = 0, 0
            self.finish_x = 1135 
            
            self.rpm = 1000.0
            self.gear = 1
            self.is_gassing = False
            self.engine_blown = False
            
            self.sanya_rpm = 1000.0
            self.sanya_gear = 1
            
            self.countdown = 3.0
            self.last_time = 0
            self.round_result = None
            self.overheat_timer = 0.4 

        def render(self, width, height, st, at):
            render = renpy.Render(1920, 1080)
            dt = st - self.last_time
            if dt > 0.1 or dt <= 0: dt = 0.016
            self.last_time = st

            retro_font = "press_start_2p.ttf" 

            font_size_upper = 20 if retro_font else 32
            font_size_lower = 18 if retro_font else 30

            tv_bg = renpy.render(Transform(renpy.displayable("bg_monitor.png"), size=(1920, 1080)), 1920, 1080, st, at)
            render.blit(tv_bg, (0, 0))

            screen_x = 276
            screen_y = 94
            screen_w = 1366
            screen_h = 768

            bg_w, bg_h = 1352, 410 
            ox = screen_x + 7 
            oy = screen_y + (screen_h - bg_h) // 2 - 10 

            bg = renpy.render(Transform(renpy.displayable("bg_drag_race.png"), size=(bg_w, bg_h)), bg_w, bg_h, st, at)
            render.blit(bg, (ox, oy))

            if self.countdown > 0:
                self.countdown -= dt
            elif self.round_result is None and not self.engine_blown:
                if self.is_gassing: self.rpm += 15000 * dt
                else: self.rpm -= 8000 * dt
                self.rpm = max(0, min(9500, self.rpm))
                
                if self.rpm >= 9500:
                    self.overheat_timer -= dt
                    if self.overheat_timer <= 0:
                        self.engine_blown = True
                        self.round_result = "lose"
                else:
                    self.overheat_timer = 0.4
                
                if self.rpm > 2000 and not self.engine_blown:
                    self.player_x += (self.rpm / 375) * (self.gear * 1.0) * dt
                
                if not self.engine_blown:
                    self.sanya_rpm += 13000 * dt
                    if self.sanya_rpm >= 8200 and self.sanya_gear < 4:
                        self.sanya_gear += 1
                        self.sanya_rpm = 4500.0
                    self.sanya_rpm = min(9000, self.sanya_rpm)
                    if self.sanya_rpm > 2000:
                        sanya_base_speed = (self.sanya_rpm / 500) * (self.sanya_gear * 1.0)
                        self.sanya_x += (sanya_base_speed + random.uniform(-0.5, 1.0)) * dt

                if self.player_x >= self.finish_x: self.round_result = "win"
                elif self.sanya_x >= self.finish_x: self.round_result = "lose"

            status_text = "DRAGRACE 1993"
            if self.countdown > 0:
                status_text = "ОЖИДАНИЕ СТАРТА"
            elif self.engine_blown or self.round_result:
                status_text = "СЛЕДУЮЩИЙ РАУНД - R"
            upper_display = "{}".format(status_text)
            upper_txt = renpy.render(Text(upper_display, size=font_size_upper, color="#ffffff", font=retro_font, outlines=[(2, "#000", 0, 0)], substitute=False), 1300, 100, st, at)
            
            upper_x = ox + (bg_w // 2) - (upper_txt.width // 2)
            render.blit(upper_txt, (upper_x, screen_y + 45))

            rounded_rpm = int(round(self.rpm / 100.0) * 100)
            lower_display = "RPM: {}  |  GEAR: {}  |  SCORE: {} - {}".format(
                rounded_rpm, self.gear, self.wins, self.losses
            )
            lower_txt = renpy.render(Text(lower_display, size=font_size_lower, color="#ffffff", font=retro_font, outlines=[(2, "#000", 0, 0)], substitute=False), 1300, 100, st, at)
            render.blit(lower_txt, (ox + 50, oy + bg_h + 25))
            
            bar_max_w = 400
            bar_h = 22
            bar_x = ox + 850
            bar_y = oy + bg_h + 23

            bg_bar_render = renpy.render(Solid("#555555", xsize=bar_max_w, ysize=bar_h), bar_max_w, bar_h, st, at)
            render.blit(bg_bar_render, (bar_x, bar_y))

            bar_w = int((self.rpm / 9500) * bar_max_w)
            
            if bar_w > 0:
                bar_color = "#ff0000" if self.rpm >= 8000 else "#00ff00"
                active_bar_render = renpy.render(Solid(bar_color, xsize=bar_w, ysize=bar_h), bar_w, bar_h, st, at)
                render.blit(active_bar_render, (bar_x, bar_y))

            if self.countdown > 0:
                current_sec = int(self.countdown) + 1
                if current_sec == 3: count_color = "#ff0000"
                elif current_sec == 2: count_color = "#ffff00"
                else: count_color = "#00ff00"
                
                count_txt = renpy.render(Text(str(current_sec), size=100, color=count_color, font=retro_font, outlines=[(4, "#000", 0, 0)]), 200, 200, st, at)
                render.blit(count_txt, (ox + (bg_w // 2) - (count_txt.width // 2), oy + (bg_h // 2) - (count_txt.height // 2)))

            car_w, car_h = 200, 134
            p_asset = renpy.displayable("explosion.png") if self.engine_blown else renpy.displayable("car_miku.png")
            img_p = renpy.render(Transform(p_asset, size=(car_w, car_h)), car_w, car_h, st, at)
            img_s = renpy.render(Transform(renpy.displayable("car_sanya.png"), size=(car_w, car_h)), car_w, car_h, st, at)
            
            render.blit(img_s, (ox + int(self.sanya_x), oy + 170))  
            render.blit(img_p, (ox + int(self.player_x), oy + 275)) 

            renpy.redraw(self, 0)
            return render

        def event(self, ev, x, y, st):
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_j and self.countdown <= 0: self.is_gassing = True
                if ev.key == pygame.K_SPACE and self.gear < 4 and self.countdown <= 0: self.gear += 1
                
                if ev.key == pygame.K_r:
                    if self.round_result:
                        if self.round_result == "win": self.wins += 1
                        else: self.losses += 1
                        if self.wins >= 2: return "win"
                        if self.losses >= 2: return "lose"
                        self.reset_round()
                    elif self.engine_blown:
                        self.losses += 1
                        if self.losses >= 2: return "lose"
                        self.reset_round()
                        
            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_j: self.is_gassing = False
            return None

screen drag_race_screen():
    modal True
    add DragRaceMinigame()