import os, sqlite3, re
import datetime

def proc_table(hand):
    '''
    Args:
        hand (str): string representation of one hand.

    Returns:
        t (list): list containing table name, max number of seats for the
        table, and the player sitting in each non-empty seat.
    '''
    is_tourney = False
    lines = helping_hand(hand)
    t = [get_table(hand), 9] + [None for i in range(10)]
    unprocessed_seats = set(range(1, 10))
    for line in lines:
        if '6-max' in line:
            t[1] = 6
        elif '2-max' in line:
            t[1] = 2
        elif 'Seat' in line:
            # "(.+) in chips" accounts for different currency symbols
            s_rx = re.compile('Seat ([0-9]+): (.+) \((.+) in chips\)')
            m = s_rx.match(line)
            if m:
                unprocessed_seats.discard(int(m.group(1)))
                t[int(m.group(1)) + 1] = m.group(2)
        if 'Tournament' in line:
            is_tourney = True
    for seat_no in unprocessed_seats:
        t[seat_no + 1] = None
        
    # convention: subtract 1 from the number of seats if it's a tourney table.
    # this is also jank and should be refactored. would be more developer
    # friendly if t[1] was a string, and probably even better still, if t
    # was a dict.
    if is_tourney:
        t[1] -= 1
    return t

def proc_hand(hand):
    '''
    Args:
        hand (str): string representation of one hand.

    Returns:
        data (list): list of tuples of the form (user_name, stat_1,
        ..., stat_n).
    '''
    
    # 3BET and 4BET track preflop only

    # Account for all variables:
    # (would still be very desirable to setup a test suite for this fn alone)
        # VAR          INDEX
        # --------------------
        # HANDS:    [x]  0
        # 3BET:     [x]  1
        # 4BET:     [x]  2
        # CBET:     [x]  3
        # 3BF:      [x]  4
        # 4BF:      [x]  5
        # CBF:      [x]  6
        # VPIP:     [x]  7
        # PFR:      [x]  8
        # STEAL:    [x]  9
        # STEALF:   [x]  10
        # O_3BET:   [x]  11
        # O_4BET:   [x]  12
        # O_CBET:   [x]  13
        # O_3BF:    [x]  14
        # O_4BF:    [x]  15
        # O_CBF:    [x]  16
        # O_VPIP:   [x]  17
        # O_PFR:    [x]  18
        # O_STEAL:  [x]  19
        # O_STEALF: [x]  20
        # T_CBET    [x]  21
        # R_CBET    [x]  22
        # T_CBET_F  [x]  23
        # R_CBET_F  [x]  24
        # O_T_CBET  [x]  25
        # O_R_CBET  [x]  26
        # O_T_CBT_F [x]  27
        # O_R_CBT_F [x]  28

    # regex triggered iff we're at the flop, turn, river, or summary.
    # note: expr shouldn't match 'HOLE CARDS' or 'SHOW DOWN.'
    state_rx = re.compile('\*\*\* [A-Z]+ \*\*\* ')

    # get player usernames
    seated = map(lambda x: x[0], get_seated(hand))

    data = dict()
    for actor in seated:
        # [1] counts the hand
        data[actor] = [1] + [0 for i in range(0,20)] + [0 for i in range(0,8)]
        # O_VPIP and O_PFR
        data[actor][17] = 1
        data[actor][18] = 1

    # state table
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    HALT = 4

    hand_state = PREFLOP
    raise_state = 0
    c_better = None
    thief = None
    lines = helping_hand(hand)
    position = 0

    for line in lines:
        if state_rx.match(line):
            # advance to next stage (flop, turn, etc.), reset raise_state
            # for new round of betting.
            hand_state += 1
            # reset raise_state at each round of betting
            raise_state = 0
            thief = None
            # c_better = None
        else:
            # get screen name for current actor
            actor = line.split(':')[0]
            # if actor not valid skip this line 
            if actor not in seated:
                pass


            elif hand_state == PREFLOP:
                # Only track position preflop for steal stat
                position += 1
                # these lines in the hand history can mess up the position var
                if 'posts small blind' in line or 'posts big blind' in line:
                    position = 0
                if len(seated) - position in range(1, 4) and raise_state == 0:
                    # O_STL
                    data[actor][19] = 1
                if thief != None and raise_state == 1:
                    # O_FOLD_TO_STEAL
                    data[actor][20] = 1
                # O_3BET
                if raise_state == 1:
                    data[actor][11] = 1
                # TODO: don't allow O_4BET or O_3BET if they're all in
                # O_4BET and O_3BF
                if raise_state == 2:
                    data[actor][12] = 1
                    data[actor][14] = 1
                # 0_4BF
                if raise_state == 3:
                    data[actor][15] = 1
                # TODO: proof this code against malicious usernames like
                # alwaysfolds22 or halls_of_calls420.
                if ' folds' in line:
                    # 3BF
                    if raise_state == 2:
                        data[actor][4] = 1
                    # 4BF
                    if raise_state == 3:
                        data[actor][5] = 1
                    # FOLD_TO_STEAL
                    if raise_state == 1 and thief != None:
                        data[actor][10] = 1
                if ' checks ' in line:
                    pass
                if ' calls ' in line:
                    # VPIP
                    data[actor][7] = 1
                if (' bets ' in line) or ('raises' in line):
                    # VPIP and PFR
                    data[actor][7] = 1
                    data[actor][8] = 1
                    # STL (O_STL condition was met)
                    if data[actor][19] == 1:
                        data[actor][9] = 1
                        thief = actor
                    # 3BET
                    if raise_state == 1:
                        data[actor][1] = 1
                    # 4BET
                    if raise_state == 2:
                        data[actor][2] = 1
                    # Make sure you increment this last
                    raise_state += 1

            elif hand_state == FLOP:
                # for cbet opportunities and cbets themselves
                # raise state must be 0 b/c it's only a cbet if you're
                # initiating the betting
                # O_CBET
                if data[actor][8] == 1 and raise_state == 0:
                    data[actor][13] = 1
                # O_CBF
                if c_better != None:
                    data[actor][16] = 1
                if (' bets ' in line) or ('raises' in line):
                    # CBET
                    if data[actor][8] == 1 and raise_state == 0:
                        data[actor][3] = 1
                        c_better = actor
                    else:
                        # if the raiser didn't raise preflop they are not
                        # cbetting, so remove the cbet state.
                        c_better = None

                    raise_state += 1
                if ' folds' in line:
                    # CBF
                    if c_better != None:
                        data[actor][6] = 1
            elif hand_state == TURN:
                # O_T_CBET
                if actor == c_better and raise_state == 0:
                    data[actor][25] = 1
                    # T_CBET
                    if (' bets ' in line) or ('raises' in line):
                        data[actor][21] = 1
                        raise_state += 1
                    else:
                        c_better = None
                elif actor == c_better and raise_state != 0:
                    # only erase c_better if they did not c_bet by the time
                    # they faced a raise (since your c_bet can be reraised)
                    if data[actor][21] == 0:
                        c_better = None
                # O_T_CBT_F
                elif c_better != None and raise_state == 1:
                    data[actor][27] = 1
                    # T_CBET_F
                    if ' folds' in line:
                        data[actor][23] = 1
            elif hand_state == RIVER:
                # O_R_CBET
                if actor == c_better and raise_state == 0:
                    data[actor][26] = 1
                    # R_CBET
                    if (' bets ' in line) or ('raises' in line):
                        data[actor][22] = 1
                        raise_state += 1
                    else:
                        c_better = None
                elif actor == c_better and raise_state != 0:
                    if data[actor][22] == 1:
                        c_better = None
                # O_R_CBET_F
                elif c_better != None and raise_state == 1:
                    data[actor][28] = 1
                    # R_CBET_F
                    if ' folds' in line:
                        data[actor][24] = 1
            else: # hand_state == HALT
                break
   
    # debugging printout, refactor this into a function
    print(hand)
    stats = ['hand', '3bet', '4bet', 'cbet', '3bf ', '4bf ', 'cbf ', 'vpip',
             'pfr ', 'stl ', 'stlf', 'tcbt', 'rcbt', 'ftcb', 'frcb'] 
    print('    user   ' + '  '.join(stats))
    for x in data:
        s1 = (map(lambda x: str(x), data[x]))
        d1 = [(x + '        ')[0:8] + ' '] + [' ' + s1[0] + '  '] + \
                map(lambda i: s1[i] + '/' + s1[i + 10] + ' ', range(1, 11)) 
        d1 += map(lambda i: s1[i] + '/' + s1[i + 4] + ' ', range(21, 25)) 
        print('  '.join(d1))

    p_ord = dict()
    for t in get_seated(hand):
        p_ord[t[0]] = t[1]

    return sorted(map(lambda x: [x] + data[x],  data.keys()), 
            key=lambda y: p_ord[y[0]])


def get_seated(hand):
    '''
    Args:
        hand (str): string representation of one hand.

    Returns:
        seated (list): list of players active in a hand and their seat numbers.
        should exclude seated players who are waiting to pay BB. each entry is
        a tuple of the form (player, seat_no).
    '''
    seated = []
    seat_rx = re.compile('Seat ([0-9]+): (.+) \((.+) in chips\)')
    lines = helping_hand(hand)
    matched_once = False
    for line in lines:
        m = seat_rx.match(line)
        if m:
            matched_once = True
            seated.append((m.group(2), int(m.group(1))))
        else:
            if matched_once:
                break
    return seated

def get_table(hand):
    '''
    Args:
        hand (str): string representation of one hand.

    Returns:
        table (str): name of table
    '''
    table_rx = re.compile("Table (\'([a-zA-Z0-9]+\s*[a-zA-Z0-9]*)\')")
    ante_rx = re.compile("Table (\'([a-zA-Z0-9]+\s*[a-zA-Z0-9]*)\')")
    lines = helping_hand(hand)
    for line in lines:
        m = table_rx.match(line)
        if m:
            return m.group(2)
    return ' '


def helping_hand(hand):
    '''
    Args:
        hand (str): string representation of one hand.

    Returns:
        lines (list): list of lines in hand w/ white space stripped.
    '''
    return map(lambda x: x.strip(), hand.split('\n'))

