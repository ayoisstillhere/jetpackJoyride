import pygame
import random
from entities.meteor import Meteor

class MeteorSystem:
    def __init__(self):
        self.meteors = []
        self.last_spawn_time = 0
        self.spawn_interval = 2000  # 2 seconds in milliseconds
        self.spawn_variance = 1000  # ±1 second variance
        self.next_spawn_time = self._calculate_next_spawn_time()
        
        # Difficulty scaling
        self.base_spawn_interval = 2000
        self.min_spawn_interval = 800  # Minimum 0.8 seconds between spawns
        
    def _calculate_next_spawn_time(self):
        """Calculate the time for the next meteor spawn with some randomness"""
        variance = random.randint(-self.spawn_variance, self.spawn_variance)
        return pygame.time.get_ticks() + self.spawn_interval + variance
    
    def update_difficulty(self, distance):
        """Adjust spawning frequency based on game progress"""
        # Increase spawn frequency as distance increases
        difficulty_factor = min(distance / 5000, 0.6)  # Max 60% difficulty increase
        self.spawn_interval = int(self.base_spawn_interval * (1 - difficulty_factor))
        self.spawn_interval = max(self.spawn_interval, self.min_spawn_interval)
    
    def should_spawn(self):
        """Check if it's time to spawn a new meteor"""
        current_time = pygame.time.get_ticks()
        return current_time >= self.next_spawn_time
    
    def spawn_meteor(self):
        """Spawn a new meteor at a random position, only if no meteors are present"""
        if len(self.meteors) == 0 and self.should_spawn():
            # Create new meteor
            new_meteor = Meteor()
            self.meteors.append(new_meteor)
            # Set next spawn time
            self.next_spawn_time = self._calculate_next_spawn_time()
            return True
        return False
    
    def update_meteors(self, paused=False, game_speed=1):
        """Update all meteors and remove inactive ones"""
        # Update existing meteors
        for meteor in self.meteors[:]:  # Create a copy to iterate safely
            meteor.update(paused, game_speed)
            
            # Remove meteors that are no longer active
            if not meteor.active:
                self.meteors.remove(meteor)
    
    def draw_meteors(self, screen):
        """Draw all active meteors"""
        for meteor in self.meteors:
            meteor.draw(screen)
    
    def check_collisions(self, player_rect):
        """Check collisions between meteors and player"""
        for meteor in self.meteors:
            if meteor.active and meteor.collides_with(player_rect):
                return meteor  # Return the colliding meteor
        return None
    
    def clear_meteors(self):
        """Remove all meteors (useful for game reset)"""
        self.meteors.clear()
    
    def get_meteor_count(self):
        """Get the number of active meteors"""
        return len(self.meteors)
    
    def get_meteors_for_ai(self):
        """Get meteor data for AI decision making"""
        return [meteor.get_hitbox() for meteor in self.meteors if meteor.active]

# Standalone functions for backward compatibility
def spawn_meteors(meteors_list, distance=0):
    """Spawn meteors using a simple list-based approach"""
    current_time = pygame.time.get_ticks()
    
    # Calculate spawn rate based on distance
    base_interval = 2500  # Base interval in milliseconds
    min_interval = 1000   # Minimum interval
    difficulty_factor = min(distance / 5000, 0.6)
    spawn_interval = int(base_interval * (1 - difficulty_factor))
    spawn_interval = max(spawn_interval, min_interval)
    
    # Check if we should spawn (simple time-based check)
    if not hasattr(spawn_meteors, 'last_spawn'):
        spawn_meteors.last_spawn = 0
    
    if current_time - spawn_meteors.last_spawn > spawn_interval:
        # Add some randomness
        if random.random() < 0.8:  # 80% chance to spawn
            meteors_list.append(Meteor())
            spawn_meteors.last_spawn = current_time

def update_meteors(meteors_list, paused=False, game_speed=1):
    """Update meteors in a list"""
    for meteor in meteors_list[:]:
        meteor.update(paused, game_speed)
        if not meteor.active:
            meteors_list.remove(meteor)

def draw_meteors(meteors_list, screen):
    """Draw meteors from a list"""
    for meteor in meteors_list:
        meteor.draw(screen)

def check_meteor_collisions(meteors_list, player_rect):
    """Check meteor collisions with player"""
    for meteor in meteors_list:
        if meteor.active and meteor.collides_with(player_rect):
            return meteor
    return None