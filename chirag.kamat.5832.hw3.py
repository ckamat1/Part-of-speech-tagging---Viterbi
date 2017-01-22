from collections import Counter

wsj_file = r'wsj00-18.tag'
lines = [line.strip() for line in open(wsj_file)]
wordtags = []
for l in lines:
    if '\t' in l:
        wordtags.append((l.split('\t')[0],l.split('\t')[1]))
    else:
        wordtags.append((l,l))

sentences = []
bigram_counts_tags = Counter()
unigram_counts_tags = Counter()
token_tag_counts = Counter()
transcounts = {}
emitcounts = {}
start_of_sentence = True

for wordtag in wordtags:
    if start_of_sentence == True:
        sentence = []
        sentence.append(('','<s>'))
        start_of_sentence = False
    if wordtag[0] == '':
        sentence.append(('',r'</s>'))
        start_of_sentence = True
        sentences.append(sentence)
    else:
        sentence.append(wordtag)


for sentence in sentences:
    unigram_tag_next = ''
    token_tag_next = ''
    for i,j in zip(sentence,sentence[1:]):
        bigram_tag = (i[1],j[1]) #prev tag and current tag bigrams
        unigram_tag = str(i[1])
        unigram_tag_next = str(j[1])
        unigram_counts_tags[unigram_tag] += 1
        bigram_counts_tags[bigram_tag] += 1
        token_tag = (i[0],i[1])
        token_tag_next = (j[0],j[1])
        token_tag_counts[token_tag] += 1
    unigram_counts_tags[unigram_tag_next] += 1
    token_tag_counts[token_tag_next] += 1

for item, count in bigram_counts_tags.iteritems():
    transcount = float(count)/ unigram_counts_tags[item[0]]
    transcounts.update({item:transcount})

for item,count in token_tag_counts.iteritems():
    emitcount = float(count) / unigram_counts_tags[item[1]]
    emitcounts.update({item:emitcount})

def viterbi(input_list,transcounts, emitcounts):
    new_input_list = ['<s>']
    new_input_list.extend(input_list)
    new_input_list.append('</s>')
    time_steps_len = len(new_input_list)
    time_steps = []
    for i in range(time_steps_len):
        time_steps.append('t' + str(i))
    states = unigram_counts_tags.keys()
    Trellis_map = {}
    for time_step in time_steps:
        for state in states:
            Trellis_map.update({(state,time_step):{'node_prob':0.0,'state':''}})
    Trellis_map[('<s>','t0')]['node_prob'] = 1.0
    for time_step, next_time_step, word in zip(time_steps,time_steps[1:],new_input_list[1:]):
        for curr_state in states:
            for next_state in states:
                trans_prob = transcounts.get((curr_state,next_state),0.0)
                emission_prob = emitcounts.get((word,next_state),0.0)
                if curr_state == '.':
                    emission_prob = 1.0
                new_prob = Trellis_map[(curr_state,time_step)]['node_prob'] * trans_prob * emission_prob
                new_state = curr_state
                old_prob = Trellis_map[(next_state,next_time_step)]['node_prob']
                old_state = Trellis_map[(next_state,next_time_step)]['state']
                if old_prob > new_prob:
                    Trellis_map.update({(next_state,next_time_step):{'node_prob':old_prob,'state':old_state}})
                else:
                    Trellis_map.update({(next_state, next_time_step): {'node_prob': new_prob, 'state': new_state}})
    classified_list = []
    time_steps.reverse()
    n = time_steps_len - 2
    state = '</s>'
    for time_step in time_steps[:n]:
        state = Trellis_map[(state,str(time_step))].get('state')
        classified_list.append(state)
    classified_list.reverse()
    return classified_list

print viterbi(['This', 'is', 'a', 'sentence', '.'], transcounts, emitcounts)
print viterbi(['This','might','produce','a','result','if','the','system','works','well','.'],transcounts,emitcounts)
print viterbi(['Can','a','can','can','a','can','?'], transcounts, emitcounts)
print viterbi(['Can','a','can','move','a','can','?'], transcounts, emitcounts)
print viterbi(['Can','you','walk','the','walk','and','talk','the','talk','?'],transcounts,emitcounts)
