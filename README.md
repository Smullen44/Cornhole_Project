# Cornhole Game (Python / Pygame) 
# Created by Sam Mullen & Daniel Russell

## Description
This project implements a  2D Cornhole game using Python and the Pygame library. 
The player can aim and throw a bean bag toward a tilted cornhole board. 
The bag follows projectile motion with gravity and can slide along the board after landing.

The goal is to land the bag on the board or into the hole.

Scoring
- 3 points – Bag goes into the hole  
- 1 point – Bag lands and stops on the board  
- 0 points – Bag misses the board  

The board is drawn at an angle to resemble a real cornhole board, and the bag may slide toward the hole
depending on where it lands.

# Requirements

This project was developed using Python 3.12.12

It also requires the Pygame library.


# Installing Python 3.12.12

Download Python 3.12.12 from the Python website:

https://www.python.org/downloads/release/python-31212/

After installing, run this in your terminal to confirm the version:

"python3 --version"


It should output something similar to:

Python 3.12.12


# Installing Pygame

Install Pygame using pip:

"pip install pygame"

or 

"pip3 install pygame"

To verify the installation run:

"python -m pygame"


# Running the Game

Go to the project folder in a terminal and run:

"python3 Midterm-Final-Code.py"


# Controls:

UP Arrow - Increase throw angle
DOWN Arrow - Decrease throw angle
Hold SPACE - Charge throw power
Release SPACE - Throw the bag
R - Reset the bag
ESC - Quit the game

# Features

- Adjustable throw angle and power
- Tilted board
- Sliding bag physics
- Hole detection and scoring system
- Reset function
- Updating score display

Thank you for playing and enjoy!
