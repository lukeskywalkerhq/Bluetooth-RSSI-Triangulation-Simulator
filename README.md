Hire Me!!!!!!
Shoffluke@gmail.com

Bluetooth Rssi Simulator

I developed this to understand how triangulation works and how i can port this over into home Assistant. Uses Pygame for graphics, and limited to 30 fps.
Use r to randomize the location of all points, and WASD to move the beacon around. The distances update once every second, as that is what i have experienced when testing
a bluetooth RSSI sensor i have. It does not use any units as i didnt do any real testing to see how accurate the ESP32 is, that being said from my understanding bluetooth Rssi
Sensor are more accute the closer you are, and the less accurte the further you are. My program does not take that into account.

For those who plan on using bluetooth to triangulate your position, Here are some tips ive learned from using this simulation:
1) avoid straight lines
   - Stright lines tend to confuse the program and tend to bounce to either side and are widly inaccurate.
2) the beacon should be on the inside
    - The beacon should be surrounded by the base stations, if the base stations are to one side or another the accuracy will suffer but will still be useable with proper filters
3) Use 4 or more beacons
     - you could probable get away with 3 but when testing, all it takes in one sensor to be a little to off and it can sway the results

If you need help or have any questions, let me know
I will be happy to help
ᓚᘏᗢ
