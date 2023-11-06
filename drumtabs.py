import json

"""
TODO
- triplet/sixlet
"""

instruments={57:'C1',49:'C2',97:'C3',55:'Sp',52:'Ch',51:'R ',53:'R ',46:'HH',92:'HH',48:'HT',47:'MT',50:'F0',45:'F1',43:'F2',41:'F3',38:'S ',42:'B ',36:'B ',35:'B ',44:'Hp'}
instrumentsHits={57:'x',49:'x',97:'x',55:'x',52:'x',51:'x',53:'b',92:'x',44:'x'}#o is default
instrumentsOrder=''.join(instruments.values())
instrumentNames={'C1':'Crash 1','C2':'Crash 2','C3':'Crash 3','Sp':'Splash','Ch':'China','R ':'Ride','HH':'Hi-hat','HT':'High tom','MT':'Mid tom','F0':'High floor tom','F1':'Floor tom 1','F2':'Floor tom 2','F3':'Floor tom 3','S ':'Snare','B ':'Bass','Hp':'Hi-hat pedal'}

def add_lines(lines,queue,queueNumChars):
	if queueNumChars==0:
		return
	elif not queue:
		restBars=queueNumChars//16
		if lines and lines[-1].startswith('(rest'):
			restBars+=int(lines[-1].split(' ')[1])
			del lines[-1]
		lines.append('(rest '+str(restBars)+' bars)\n')
	else:
		queue=dict(sorted(queue.items(), key=lambda item: instrumentsOrder.index(item[0])))
		newLines=[]
		for item in queue.items():
			notes=item[1].replace('DD','d')#.replace('t-t-t-','t-')
			notes='|'.join(notes[j:j+16] for j in range(0,len(notes),16))
			newLines.append(item[0]+'|'+notes+'|')
		newLines.append('')
		lines+=newLines

def get_tab(fn):
	with open(fn,'r') as f:
		j=json.load(f)
	
	lines=[]
	queue={}
	queueNumChars=0
	usedFrets=set()
	tupletMeasures=set()
	
	for i in range(len(j['measures'])):
		m=j['measures'][i]
		#print(json.dumps(m, indent=4))
		
		if 'marker' in m or queueNumChars>=4*16:
			add_lines(lines,queue,queueNumChars)
			queue={}
			queueNumChars=0
		if 'marker' in m:
			lines.append(m['marker']['text'])
		
		voices={}
		
		for vi in range(len(m['voices'])):
			v=m['voices'][vi]
			if 'beats' not in v:
				continue
			
			measure={}
			measureNumChars=0
			
			for b in v['beats']:
				t=b['type']
				#if t>16 or 'dotted' in b or 'tuplet' in b:
				if 'tuplet' in b:
					#print(b)
					tupletMeasures.add(i+1)
				#numChars=(24//t) if 'dotted' in b else (32//t) if 'tuplet' in b else 0 if 'tupletStop' in b else (16//t)
				numChars=(24//t) if 'dotted' in b else (16//t)
				noteInstruments=set()
				for n in b['notes']:
					#print(n)
					if 'rest' in n or 'tie' in n:
						continue
					fret=n['fret']
					if fret not in instruments:
						print('\n'.join(lines))
						print('unknown instrument id',fret,'measure',i+1)
						print(b)
						exit(1)
					usedFrets.add(fret)
					instrument=instruments[fret]
					noteInstruments.add(instrument)
					if instrument not in measure:
						measure[instrument]='-'*measureNumChars
					#queue[instrument]+='d' if t==32 else 't' if 'tuplet' in b else instrumentsHits[fret] if fret in instrumentsHits else 'o'
					measure[instrument]+='D' if t==32 else instrumentsHits[fret] if fret in instrumentsHits else 'o'
					measure[instrument]+='-'*(numChars-1)
					
				for instrument in measure.keys():
					if instrument not in noteInstruments:
						measure[instrument]+='-'*numChars
				
				measureNumChars+=numChars
			
			voices.update(measure)
		
		for instrument in queue:
			if instrument not in voices:
				voices[instrument]='-'*measureNumChars
		
		for instrument in voices:
			queue[instrument]=(queue[instrument] if instrument in queue else '') + voices[instrument]
		
		queueNumChars+=measureNumChars
	
	if queueNumChars>0:
		add_lines(lines,queue,queueNumChars)
	
	if tupletMeasures:
		lines.append('tupletMeasures: '+str(sorted(list(tupletMeasures)))+'\nneed to manually correct them\n')
	
	if 'D' in str(lines):
		lines.append('found 32nd notes split to different instruments "D"\nneed to manually correct\n')
	
	while '(is repeat)' in lines:
		r=lines.index('(is repeat)')
		while lines[r+1]!='':
			del lines[r+1]
		lines[r]='(repeat above)'
	
	header=[]
	header.append(fn.split('.')[0]+'\n')
	instrumentInfo=dict()
	
	for fret in usedFrets:
		instrument=instruments[fret]
		instrumentInfo[instrument]=instrumentNames[instrument]
	
	instrumentInfo=dict(sorted(instrumentInfo.items(), key=lambda item: instrumentsOrder.index(item[0])))
	for ii in instrumentInfo.items():
		header.append(' = '.join(ii))
	header.append('')
	
	return '\n'.join(header+lines)

def write_tab(fn):
	s=get_tab(fn)
	print(s)
	with open(fn.split(".")[0]+".txt", "w") as f:
		f.write(s)

#write_tab('Pixies - Where Is My Mind.json')
#write_tab('Slipknot - Unsainted.json')
#write_tab('Slipknot - Psychosocial.json')
#write_tab('Babymetal - IN the NAME OF.json')
write_tab('Babymetal - Gimme Choco.json')
