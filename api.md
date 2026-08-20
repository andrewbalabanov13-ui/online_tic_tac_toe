First, The client sends enter_queue then after, puts the | brackets and their name
example: enter_queue|Bob

Then, every time they recieve and message starting with relay|, then remove relay| from the message and send it to the server

after that, if you get make_first_move, then you move by typing move|x|y

finnaly, when you get a message to move_update_relay, the client, you input an x bigger than -1, smaller than 21, and same for y
ex: move|3|4
and if you get update, then you just update the board