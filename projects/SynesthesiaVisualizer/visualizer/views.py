from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
import json

LETTER_COLORS = {
    # Letters
    'a': '#FF0000',  # Red
    'b': '#0052EF',  # Blue
    'c': '#0044BE',  # Dark Blue
    'd': '#FFFFFF',  # White
    'e': '#ff9dda',  # Hot Pink
    'f': '#e50063',  # Blue Violet
    'g': '#00630d',  # Orange Red
    'h': '#bde180',  # Cyan
    'i': '#1000db',  # Deep Pink
    'j': '#ff8d00',  # Chartreuse
    'k': '#ffdb70',  # Dark Violet
    'l': '#7e3907',  # Dark Orange
    'm': '#030063',  # Dodger Blue
    'n': '#6e5777',  # Light Pink
    'o': '#ae1813',  # Lime Green
    'p': '#f700a2',  # Medium Orchid
    'q': '#c119b7',  # Tomato
    'r': '#948b37',  # Royal Blue
    's': '#ffff41',  # Medium Purple
    't': '#0162b0',  # Medium Sea Green
    'u': '#bc00ac',  # Indian Red
    'v': '#cccccc',  # Medium Turquoise
    'w': '#d0c45e',  # Medium Violet Red
    'x': '#52010c',  # Midnight Blue
    'y': '#f4e35a',  # Khaki
    'z': '#a2a2a2',  # Saddle Brown
    
    # Numbers
    '0': '#000000',  # Lavender
    '1': '#ff1700',  # Light Salmon
    '2': '#64c2ff',  # Pale Green
    '3': '#ffd000',  # Plum
    '4': '#784a02',  # Khaki
    '5': '#0500b9',  # Sky Blue
    '6': '#a100dc',  # Orange
    '7': '#ff8700',  # Light Sea Green
    '8': '#be0300',  # Fire Brick
    '9': '#b00087',  # Indigo
    
    # Special characters
    ' ': '#000000',  # White for spaces
    '.': '#000000',  # Black for periods
    ',': '#000000',  # Gray for commas
    '!': '#000000',  # Gold for exclamation marks
    '?': '#000000',  # Plum for question marks

    # Mathematical Symbols - using shades of purple and blue for consistency
    '±': '#4B0082',  # Indigo
    '√': '#9400D3',  # Dark Violet
    'π': '#8B008B',  # Dark Magenta
    '%': '#483D8B',  # Dark Slate Blue
    '∞': '#9370DB',  # Medium Purple
    '∫': '#4169E1',  # Royal Blue
    '∑': '#800080',  # Purple
    '∏': '#9932CC',  # Dark Orchid
    'Δ': '#8A2BE2',  # Blue Violet
    '≈': '#7B68EE',  # Medium Slate Blue
    '≠': '#6A5ACD',  # Slate Blue
    '≤': '#0000CD',  # Medium Blue
    '≥': '#0000FF',  # Blue
}

def dim_color(hex_color, dim_factor=0.8):
    """
    Dim a hex color by multiplying its RGB components by dim_factor
    """
    # Remove the '#' and convert to RGB
    hex_str = hex_color.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    
    # Apply dimming factor
    r = int(r * dim_factor)
    g = int(g * dim_factor)
    b = int(b * dim_factor)
    
    # Convert back to hex
    return f'#{r:02x}{g:02x}{b:02x}'

def get_color_brightness(hex_color):
    """
    Calculate the perceived brightness of a color (0-255)
    Using the formula from W3C accessibility guidelines
    """
    hex_str = hex_color.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000

def create_background_shade(hex_color):
    """
    Create a background shade based on the color brightness.
    For dark colors, lighten them
    For light colors, darken them
    For white color, return a light gray
    """
    # Special case for white color
    if hex_color.upper() == '#FFFFFF':
        return 'rgba(200, 200, 200, 0.3)'  # Light gray with transparency
        
    brightness = get_color_brightness(hex_color)
    hex_str = hex_color.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    
    if brightness > 128:  # Light color
        # Darken by 10%
        r = int(r * 0.9)
        g = int(g * 0.9)
        b = int(b * 0.9)
    else:  # Dark color
        # Lighten by mixing with white
        r = int(r + (255 - r) * 0.2)
        g = int(g + (255 - g) * 0.2)
        b = int(b + (255 - b) * 0.2)
    
    # Add transparency by converting to rgba
    return f'rgba({r}, {g}, {b}, 0.15)'

def get_active_profile(request):
    profile_id = request.session.get('active_profile')
    if profile_id:
        try:
            return Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            pass
    # Get default profile or create one
    default_profile = Profile.objects.first()
    if not default_profile:
        default_profile = Profile.objects.create(
            name="Default Profile",
            color_settings=json.dumps(LETTER_COLORS)
        )
    request.session['active_profile'] = default_profile.id
    return default_profile

def create_profile(request):
    if request.method == 'POST':
        name = request.POST.get('profile_name', '').strip()
        if name:
            # Get the current active profile's colors to use as a starting point
            current_profile = get_active_profile(request)
            current_colors = current_profile.get_colors()
            
            # Create new profile with copied colors
            profile = Profile.objects.create(
                name=name,
                color_settings=json.dumps(current_colors)  # Use current profile's colors instead of defaults
            )
            request.session['active_profile'] = profile.id
    return redirect('visualizer:landing')

def switch_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    request.session['active_profile'] = profile.id
    return redirect('visualizer:landing')

def delete_profile(request, profile_id):
    if Profile.objects.count() > 1:  # Prevent deleting the last profile
        Profile.objects.filter(id=profile_id).delete()
        if request.session.get('active_profile') == profile_id:
            # Switch to another profile if the active one was deleted
            new_profile = Profile.objects.first()
            request.session['active_profile'] = new_profile.id
    return redirect('visualizer:landing')

def landing(request):
    """Landing page view that shows all available visualizers"""
    active_profile = get_active_profile(request)
    profiles = Profile.objects.all().order_by('name')
    return render(request, 'visualizer/landing.html', {
        'active_profile': active_profile,
        'profiles': profiles,
    })

def grapheme_color(request):
    """View for the grapheme-color visualizer (previously the home view)"""
    colored_text = []
    original_text = ''
    active_profile = get_active_profile(request)
    profiles = Profile.objects.all().order_by('name')
    colors = active_profile.get_colors()
    
    if request.method == 'POST':
        text = request.POST.get('text', '')[:500]
        original_text = text
        
        # Process text word by word
        words = text.split()
        for word in words:
            if not word:  # Skip empty words
                continue
                
            # Process first character of word and get its background
            first_char = word[0]
            is_number = first_char.isdigit()
            first_color = colors.get(first_char.lower(), '#000000')
            word_background = 'transparent' if is_number else create_background_shade(first_color)
            
            # First character
            colored_text.append({
                'char': first_char, 
                'color': first_color,
                'background': word_background
            })
            
            # Process rest of word with dimmed colors but same background
            for char in word[1:]:
                is_number = char.isdigit()
                color = colors.get(char.lower(), '#000000')
                char_color = color if is_number else dim_color(color)
                
                colored_text.append({
                    'char': char, 
                    'color': char_color,
                    'background': word_background  # Use same background as first letter
                })
            
            # Add space between words
            colored_text.append({
                'char': ' ', 
                'color': colors.get(' ', '#000000'),
                'background': 'transparent'
            })
    
    return render(request, 'visualizer/grapheme_color.html', {
        'colored_text': colored_text,
        'original_text': original_text,
        'active_profile': active_profile,
        'profiles': profiles,
        'colors': colors,
    })

def sequence_space(request):
    """View for the sequence-space visualizer"""
    active_profile = get_active_profile(request)
    profiles = Profile.objects.all().order_by('name')
    return render(request, 'visualizer/new_pages/sequence_space.html', {
        'active_profile': active_profile,
        'profiles': profiles,
    })

def ticker_tape(request):
    """View for the ticker-tape visualizer"""
    active_profile = get_active_profile(request)
    profiles = Profile.objects.all().order_by('name')
    return render(request, 'visualizer/new_pages/ticker_tape.html', {
        'active_profile': active_profile,
        'profiles': profiles,
    })

def visualize_text(request):
    text = request.POST.get('text', '')[:500]
    colored_text = []
    active_profile = get_active_profile(request)
    colors = active_profile.get_colors()
    
    # Process text word by word
    words = text.split()
    for word in words:
        if not word:  # Skip empty words
            continue
            
        # Process first character of word and get its background
        first_char = word[0]
        is_number = first_char.isdigit()
        first_color = colors.get(first_char.lower(), '#000000')
        word_background = 'transparent' if is_number else create_background_shade(first_color)
        
        # First character
        colored_text.append({
            'char': first_char, 
            'color': first_color,
            'background': word_background
        })
        
        # Process rest of word with dimmed colors but same background
        for char in word[1:]:
            is_number = char.isdigit()
            color = colors.get(char.lower(), '#000000')
            char_color = color if is_number else dim_color(color)
            
            colored_text.append({
                'char': char, 
                'color': char_color,
                'background': word_background  # Use same background as first letter
            })
        
        # Add space between words
        colored_text.append({
            'char': ' ', 
            'color': colors.get(' ', '#000000'),
            'background': 'transparent'
        })
    
    return render(request, 'visualizer/result.html', {
        'colored_text': colored_text,
        'original_text': text,
    })

@csrf_exempt
def save_word_shading(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        enabled = data.get('enabled', False)
        active_profile = get_active_profile(request)
        active_profile.word_shading_enabled = enabled
        active_profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def save_bright_letters(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        enabled = data.get('enabled', False)
        letters = data.get('letters', '').lower().split(',')
        letters = [l.strip() for l in letters if l.strip()]
        
        active_profile = get_active_profile(request)
        active_profile.bright_letters_enabled = enabled
        if enabled:
            active_profile.set_bright_letters(letters)
        active_profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def get_colors_for_text(request):
    data = json.loads(request.body)
    text = data.get('text', '')
    active_profile = get_active_profile(request)
    colors = active_profile.get_colors()
    bright_letters = active_profile.get_bright_letters() if active_profile.bright_letters_enabled else set()
    
    colored_text = []
    current_word = []
    current_background = 'transparent'
    
    words = text.split()
    for i, word in enumerate(words):
        # Process each word
        for j, char in enumerate(word):
            char_lower = char.lower()
            is_number = char.isdigit()
            color = colors.get(char_lower, '#000000')
            
            # If this is the first letter of the word
            if j == 0:
                # Only set background if word shading is enabled and it's not a number
                if active_profile.word_shading_enabled and not is_number:
                    current_background = create_background_shade(color)
                else:
                    current_background = 'transparent'
            
            # Add the character with appropriate color
            char_color = color
            if j > 0 and active_profile.word_shading_enabled and not is_number:
                # Don't dim if it's a bright letter
                if char_lower not in bright_letters:
                    char_color = dim_color(color)
                
            colored_text.append({
                'char': char,
                'color': char_color,
                'background': current_background if char_lower not in bright_letters else create_background_shade(color)
            })
        
        # Add extra space between words (but not after the last word)
        if i < len(words) - 1:
            colored_text.append({'char': ' ', 'color': colors.get(' ', '#000000'), 'background': 'transparent'})
            colored_text.append({'char': ' ', 'color': colors.get(' ', '#000000'), 'background': 'transparent'})
            colored_text.append({'char': ' ', 'color': colors.get(' ', '#000000'), 'background': 'transparent'})
    
    return JsonResponse({'colored_text': colored_text})

def faq(request):
    """View for the FAQ page"""
    return render(request, 'visualizer/faq.html')

def color_settings(request):
    active_profile = get_active_profile(request)
    return render(request, 'visualizer/color_settings.html', {
        'colors': active_profile.get_colors(),
        'profile': active_profile
    })

def save_colors(request):
    if request.method == 'POST':
        active_profile = get_active_profile(request)
        new_colors = {}
        for key, value in request.POST.items():
            if key.startswith('color_'):
                char = key[6:]
                new_colors[char] = value
        active_profile.set_colors(new_colors)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def color_statistics(request):
    """View for displaying color statistics across all profiles"""
    from collections import defaultdict
    from colorsys import rgb_to_hsv

    # Helper function to convert hex to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Helper function to get color name based on HSV
    def get_color_name(h, s, v):
        if s < 0.1:  # For very low saturation
            if v < 0.3: return 'black'
            if v > 0.9: return 'white'
            return 'gray'
        
        # Basic color wheel divided into 8 parts
        hue_names = [
            'red', 'orange', 'yellow', 'green',
            'cyan', 'blue', 'purple', 'pink'
        ]
        hue_index = int((h * 8) % 8)
        color_name = hue_names[hue_index]
        
        # Add intensity modifiers
        if v < 0.3: return f'dark {color_name}'
        if v > 0.9: return f'bright {color_name}'
        if s > 0.8: return f'vivid {color_name}'
        return color_name

    # Get all profiles and their color settings
    profiles = Profile.objects.all()
    color_stats = defaultdict(list)
    
    # Collect all colors for each character
    for profile in profiles:
        colors = profile.get_colors()
        for char, color in colors.items():
            # Only process letters and numbers
            if not (char.isalnum() and len(char) == 1):
                continue
            rgb = hex_to_rgb(color)
            hsv = rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            color_stats[char].append({
                'hex': color,
                'hsv': hsv,
                'name': get_color_name(hsv[0], hsv[1], hsv[2])
            })
    
    # Calculate most common colors and their percentages
    stats_result = {}
    for char, colors in color_stats.items():
        if not colors:
            continue
            
        # Count occurrences of each color name
        color_counts = defaultdict(int)
        for c in colors:
            color_counts[c['name']] += 1
        
        # Calculate percentages and find most common
        total = len(colors)
        color_percentages = {
            name: (count / total * 100)
            for name, count in color_counts.items()
        }
        
        # Sort by percentage
        sorted_colors = sorted(
            color_percentages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get sample hex colors for each name
        color_samples = {}
        for color in colors:
            if color['name'] not in color_samples:
                color_samples[color['name']] = color['hex']
        
        stats_result[char] = {
            'total_profiles': total,
            'colors': [
                {
                    'name': name,
                    'percentage': percentage,
                    'sample_hex': color_samples[name]
                }
                for name, percentage in sorted_colors
            ]
        }
    
    # Separate letters and numbers
    letter_stats = {
        char: data for char, data in stats_result.items()
        if char.isalpha()
    }
    number_stats = {
        char: data for char, data in stats_result.items()
        if char.isdigit()
    }
    
    return render(request, 'visualizer/statistics.html', {
        'letter_stats': letter_stats,
        'number_stats': number_stats,
        'profiles_count': profiles.count(),
    })
