import csv

with open('Fall 2016 faculty staff list.csv', 'rb') as csvfile:
    rr = csv.reader(csvfile, delimiter=',')
    for row in rr:
        op_file = open (row[3]+'.md', 'w')
        op_file.write('---' + '\n')
        op_file.write('UVA_id: ' + row[3]+ '\n')
        op_file.write('lastname: ' + row[0].split(' ')[1] + '\n')
        op_file.write('name: ' + row[0].split(' ')[0] + '\n')
        op_file.write('general_position: gradstudent' + '\n')
        op_file.write('position: Graduate Student' + '\n')
        op_file.write('office: ' + row[2] + ' Hall' + '\n')
        op_file.write('phone: 434-' + row[1] + '\n')
        op_file.write('email: ' + row[3] +'@virginia.edu' + '\n')
        op_file.write('image:' + '\n')
        op_file.write('personal_page:' + '\n')
        op_file.write('interests: #Any and all narrower research interests' + '\n')
        op_file.write('\n')
        op_file.write('---' + '\n')
        
