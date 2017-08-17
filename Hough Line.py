import cv2
import numpy as np

ratio2 = 3
kernel_size = 3
lowThreshold = 30

img = cv2.imread('./Data/S_03.jpg')
sudoku1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

r, c = sudoku1.shape
out_row = 500
sudoku1 = cv2.resize(sudoku1, (int(out_row * float(c)/r), out_row))
im = sudoku1.copy()

sudoku1 = cv2.blur(sudoku1, (3,3))
cv2.imshow('imread', sudoku1)
cv2.waitKey(0)

edges = cv2.Canny(sudoku1, lowThreshold, lowThreshold * ratio2, kernel_size)
cv2.imshow('Canny Edges',edges)
cv2.waitKey(0)


# Apply Hough Line Transform, return a list of rho and theta
lines = cv2.HoughLines(edges, 2, cv2.cv.CV_PI/180, 300, 0, 0)

if (lines is not None):
    lines = lines[0]
    lines = sorted(lines, key = lambda z: z[0])
    
    # Define the position of horizontal and vertical line
    pos_hori = 0
    pos_vert = 0
    
    # Create a list to store new bundle of lines
    New_lines = []
    # Store intersection points
    Points = []
    
    for rho, theta in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        
        #If b > 0.5, the angle must be greater than 45. So, we consider it as a vertical line
        if (b > 0.5):
            #Check the position
            if(rho - pos_hori > 10):
                #Update the position
                pos_hori = rho
                # Saving new line, 0 is horizontal line, 1 is vertical line
                New_lines.append([rho, theta, 0])
        else:
            if(rho - pos_vert > 10):
                pos_vert = rho
                New_lines.append([rho, theta, 1])
    
    for i in range(len(New_lines)):
        if (New_lines[i][2] == 0):
            for j in range(len(New_lines)):
                if (New_lines[j][2] == 1):
                    theta1 = New_lines[i][1]
                    theta2 = New_lines[j][1]
                    
                    p1 = New_lines[i][0]
                    p2 = New_lines[j][0]
                    
                    xy = np.array([[np.cos(theta1), np.sin(theta1)],
                                   [np.cos(theta2), np.sin(theta2)]])
                    p = np.array([p1, p2])
                    
                    res = np.linalg.solve(xy, p)
                    
                    Points.append(res)
    # Sanity check                
    if (len(Points) == 100):
        sudoku1 = cv2.adaptiveThreshold(sudoku1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV, 101, 1)
        
        for i in range(0, 9):
            for j in range(0, 9):
                # j+ i*10 will follow 0 1 2 3 4 5 6 7 8
                #                    10 11 12 13 14 15 16 17 18
                # 
                
                y1 = int(Points[j+i*10][1] + 5)
                # +11? We need opposite vertices to draw a rectangle
                y2 = int(Points[j+i*10 +11][1] - 5)
                
                x1 = int(Points[j+i*10][0] + 5)
                x2 = int(Points[j+i*10+11][0] - 5)
                
                
                cv2.rectangle(im, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow('Hough Lines', im)
    cv2.waitKey(0)
