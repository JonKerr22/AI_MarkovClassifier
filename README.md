# AI_MarkovClassifier
http://slazebni.cs.illinois.edu/fall17/assignment4.html

notes from watching lecture:
Part 1 is same digit classification from mp3 but with new math
using perceptron instead of Naive Bayes, aka now have look at pixel, 
  multiply by precalculated weight, and apply a step function
one vs others classifer, in slides for more details, 33/60
  x vector is a vector of pixels
  Wc weight vector for digit c
slide 33 is the entire first half of MP4, in terms of the math you need to do

2nd half is pong, but you have an AI just bouncing it off walls
is slightly random so need to make probabilities of where ball will go
doesn't need to be perfect, but should be able to reliably get 6-10 bounces per game
basically want to see ball in some place, with some velocity, predict where it will go, then move paddle to hit
Q-learning is from lectures on November 28th and 30th
