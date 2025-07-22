from django.db import models
import json
from django.contrib.auth.models import User

class Profile(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    word_shading_enabled = models.BooleanField(default=False)
    bright_letters_enabled = models.BooleanField(default=False)
    bright_letters = models.CharField(max_length=100, default='')  # Store bright letters as a comma-separated string
    color_settings = models.TextField(default='{}')  # Stores JSON of color settings
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_colors(self):
        return json.loads(self.color_settings)
    
    def set_colors(self, colors_dict):
        self.color_settings = json.dumps(colors_dict)
        self.save()
        
    def get_bright_letters(self):
        return set(self.bright_letters.split(',')) if self.bright_letters else set()
    
    def set_bright_letters(self, letters):
        self.bright_letters = ','.join(sorted(letters))
        self.save()
        
    def __str__(self):
        return self.name
