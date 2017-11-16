

#Given two python dictionaries = {key:{val: item, clock:number, timestamp:time}}
#merge the two based on their vector clock FIELD=CLOCK
#if a tie occurs, break the tie with their timestamp

def merge(dict1, dict2):
    #print("merging", dict1, dict2 )

    for key in dict1:
        #print(key)
        if key in dict2:
            #print(dict1[key], dict[key])
            winner = compare(dict1[key], dict2[key])
            #print("setting winner in dict1")
            dict1[key] = winner
        else:
            #print("in else")
            dict2[key] = dict1[key]
    for key in dict2:
        if key in dict1:
            winner = compare(dict1[key], dict2[key])
            dict2[key] = winner
        else:
            dict1[key] = dict2[key]
    return dict1

#compares the values of the two values for the same key
def compare(key1, key2):
    clock1 = int(key1['clock'])
    clock2 = int(key2['clock'])
    #print("comparing  c1 c2", clock1, clock2)
    if clock1 > clock2:
        return key1
    elif clock1 < clock2:
        return key2
    elif clock1 == clock2:
        # tie break timestamps
        if key1['timestamp'] > key2['timestamp']:
            print("tie breaker", key1['timestamp'], key2['timestamp'])
            return key1
        else:
            return key2


#TEST CASES:

#test dict1 with 1 key:value
#test dict2 with 1 keyvalue different from dict1

#result should be a dict with both sets of information

dict1 = {'key1': {'val': 'dict1', 'clock': '1', 'timestamp': '15'}}
dict2 = {'key2': {'val': 'dict1', 'clock': '2', 'timestamp': '15'}}

dict_result = merge(dict1, dict2)
print(dict_result)

dict1 = dict_result
dict_result = merge(dict1, {'key2': {'val': 'merge with 3', 'clock': '3', 'timestamp': '15'}})

print(dict_result)

#test dict2 with same value but newer clock



dict1 = {'key1': {'val': 'dict1', 'clock': '1', 'timestamp': '15'}}
dict2 = {'key1': {'val': 'dict1', 'clock': '1', 'timestamp': '16'}}
#timestamp should win



dict1 ={'key1': {'val': 'dict1', 'clock': '1', 'timestamp': '15'},
        'key3': {'val': 'dict1', 'clock': '2', 'timestamp': '15'},
        'key5': {'val': 'dict1', 'clock': '3', 'timestamp': '15'},
        'key7': {'val': 'dict1', 'clock': '4', 'timestamp': '15'},
        'key9': {'val': 'dict1', 'clock': '4', 'timestamp': '15'},
        }

dict2 = {'key2': {'val': 'dict1', 'clock': '4', 'timestamp': '15'},
         'key4': {'val': 'dict2', 'clock': '2', 'timestamp': '16'},
         'key6': {'val': 'dict2', 'clock': '0', 'timestamp': '15'},
         'key8': {'val': 'dict2', 'clock': '0', 'timestamp': '15'},
         'key10': {'val': 'dict2', 'clock': '0', 'timestamp': '15'},
         }

result = merge(dict1, dict2)

for key in result:
    print(key, result[key])