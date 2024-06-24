def parse_markdown_result(markdown_text, n_headers, first_header=''):
    texts = markdown_text.split("\n")
    first_index = -1
    row_index = 0
    results = []
    for i in range(0, len(texts)):
        text = texts[i].strip().replace('\r', '').replace('\n', '<br/>').replace(',', '，')
        arr = text.split('|')
        if (len(arr) >= n_headers):
            if (first_index == -1):
                if (len(arr) > n_headers):
                    if (len(first_header) == 0 or (len(first_header) > 0 and arr[1].find(first_header) >= 0)):
                        first_index = 1
                else:
                    if (len(arr) == n_headers):
                        if (len(first_header) == 0 or (len(first_header) > 0 and arr[0].find(first_header) >= 0)):
                            first_index = 0
            else:
                # print(arr, first_index)
                row_index = row_index + 1
                if (row_index > 1):
                    row_data = []
                    for j in range(0, n_headers):
                        if(first_index + j>=len(arr)):
                            break
                        row_data.append(arr[first_index + j].strip())
                    results.append(row_data)
    if(len(results)==0 and markdown_text.find('|')>=0 and not markdown_text.__contains__('---')):
        header = '|'
        for i in range(n_headers):
            if(i==0 and len(first_header)>0):
                header+=first_header+'|'
            else:
                header+='XXX|'
        header+='\n|'
        for i in range(n_headers):
            header += '---|'
        return parse_markdown_result(header+'\n'+markdown_text,n_headers,first_header=first_header)
    return results