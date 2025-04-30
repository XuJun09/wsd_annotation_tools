import gradio as gr
import os
import pandas as pd
import pickle

# 检测工作目录状态
if(not os.path.exists('./raw_data/')):
    os.mkdir('./raw_data')
if(not os.path.exists('./annotated_data/')):
    os.mkdir('./annotated_data')

# 初始化文件列表，对已经标注的文件打勾
file_list = os.listdir("./raw_data/")
file_list = [file.split('.')[0] for file in file_list if file.endswith(".csv")]
# 用于记录文件进度的字典
try:
    file_progress = pickle.load(open('./file_progress.pkl','rb'))
except:
    file_progress = {file_name:[0,0] for file_name in file_list}
# 初始化文件进度显示
deleted_files = []
for file_name in file_progress.keys():
    if(not file_name in file_list): # 文件被删除了
        deleted_files.append(file_name)
    elif(file_progress[file_name][1] == 0): # 没有被读取过文件长度
        f = open('./raw_data/' + file_name + '.csv', 'r', encoding='utf-8')
        file_progress[file_name][1] = len(f.readlines()) - 2 # 去掉表头和最后的空行
        f.close()
    elif(file_progress[file_name][0] == file_progress[file_name][1]):
        file_list[file_list.index(file_name)] = '★ ' + file_name
    elif(file_progress[file_name][0] == 0):
        continue
    else:
        file_list[file_list.index(file_name)] = '☆ ' + file_name
for del_file in deleted_files:
    del file_progress[del_file]
del deleted_files

# 将更新总长度之后的文件进度序列化
pickle.dump(file_progress,open('./file_progress.pkl','wb'))

word_meaning_map = pickle.load(open('./word_meaning_map.pkl','rb'))
try:
    word_example_map = pickle.load(open('./word_example_map.pkl','rb'))
except:
    word_example_map = word_meaning_map

def highlight_target_word(current_word,current_text):
    for i in range(len(current_text)):
        if(current_text[i:i+len(current_word)] == current_word):
            return current_text[:i] + '【' + current_word + '】' + current_text[i+len(current_word):]
    return current_text

with gr.Blocks() as demo:
    dataframe = gr.State()
    with gr.Row():
        with gr.Column(scale=5):
            choose_file = gr.Dropdown(file_list, label="文件列表", value= '')
        with gr.Column(scale=1):
            index = gr.Number(label="当前进度",interactive=False)
        with gr.Column(scale=1):
            full_length = gr.Number(label="待标注句子总数",interactive=False)
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            current_word = gr.Textbox(label="当前词")
        with gr.Column(scale=5):
            current_meaning = gr.Textbox(label="模型判断词义")
    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            current_text = gr.Textbox(label="当前文本")
        with gr.Column(scale=2):
            examples = gr.DataFrame(visible=False)
        
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            tf_state = gr.Radio(label="词义标注是否正确",choices=["是","否"],value="是")
        with gr.Column(scale=5):
            choose_meaning = gr.Dropdown(label="选择词义",visible=False)
    with gr.Row():
        with gr.Column():
            prev_sent = gr.Button("上一句")
        with gr.Column():
            next_sent = gr.Button("下一句")
    with gr.Row():
        save_btn = gr.Button("保存")
    
    @choose_file.change(inputs=[choose_file,dataframe,current_word,index], 
                        outputs=[dataframe,
                                 current_word,
                                 current_meaning,
                                 current_text,
                                 tf_state,
                                 choose_meaning,
                                 examples,
                                 choose_file,
                                 index,
                                 full_length])
    def load_file(choose_file,dataframe,current_word,index):
        global word_meaning_map, word_example_map, file_list, annotated_list, file_progress
        if(dataframe is None):
            pass
        else:
            if(isinstance(dataframe,pd.DataFrame)):
                dataframe.to_csv("./annotated_data/" + current_word + ".csv",index=False)
                file_progress[current_word][0] = index
                pickle.dump(file_progress,open('./file_progress.pkl','wb'))
            else:
                dataframe = None
        # 更新文件列表
        annotated_list = os.listdir("./annotated_data/")
        annotated_list = [file.split('.')[0] for file in annotated_list if file.endswith(".csv")]
        for indx in range(len(file_list)):
            file_list[indx] = file_list[indx].strip('★☆ ')
            if(file_progress[file_list[indx].strip('★☆ ')][0] == file_progress[file_list[indx].strip('★☆ ')][1]):
                file_list[indx] = '★ ' + file_list[indx]
            elif(file_progress[file_list[indx].strip('★☆ ')][0] == 0):
                continue
            else:
                file_list[indx] = '☆ ' + file_list[indx]
        if(choose_file.startswith('★')):
            file_name = "./annotated_data/" + choose_file.strip('★ ') + ".csv"
            dataframe = pd.read_csv(file_name)
        elif(choose_file.startswith('☆')):
            file_name = "./annotated_data/" + choose_file.strip('☆ ') + ".csv"
            dataframe = pd.read_csv(file_name)
        else:
            file_name = "./raw_data/" + choose_file + ".csv"
            dataframe = pd.read_csv(file_name)
            dataframe['true_meaning'] = dataframe['meaning']
        word = choose_file.strip('★☆ ')
        return (dataframe,
                dataframe['word'][0],
                dataframe['meaning'][file_progress[word][0]],
                highlight_target_word(dataframe['word'][0],dataframe['sentence'][file_progress[word][0]]),
                gr.update(value = "是" if(dataframe['true_meaning'][file_progress[word][0]] == dataframe['meaning'][file_progress[word][0]]) else "否"),
                gr.update(choices = word_meaning_map[dataframe['word'][0]],value = dataframe['true_meaning'][file_progress[word][0]]),
                gr.update(value = pd.DataFrame({"释义与例句":word_example_map[dataframe['word'][0]]}), visible=True),
                gr.update(choices = file_list),
                file_progress[word][0],
                file_progress[word][1])
    
    
    @tf_state.change(inputs=[tf_state],outputs=[choose_meaning])
    def tf_state_change(tf_state):
        if(tf_state == "是"):
            return gr.update(visible=False)
        else:
            return gr.update(visible=True)
    
    @prev_sent.click(inputs=[dataframe,index],outputs=[dataframe,current_meaning,current_text,tf_state,choose_meaning,index])
    def prev_sent_click(dataframe,index):
        if(index == 0):
            gr.Info("已到达第一句")
            return (dataframe,
                    dataframe['meaning'][0],
                    highlight_target_word(dataframe['word'][0],dataframe['sentence'][0]),
                    gr.update(value = "是" if(dataframe['true_meaning'][0] == dataframe['meaning'][0]) else "否"),
                    gr.update(value = dataframe['true_meaning'][0]),
                    0)
        else:
            return (dataframe,
                    dataframe['meaning'][index-1],
                    highlight_target_word(dataframe['word'][0],dataframe['sentence'][index-1]),
                    gr.update(value = "是" if(dataframe['true_meaning'][index-1] == dataframe['meaning'][index-1]) else "否"),
                    gr.update(value = dataframe['true_meaning'][index-1]),
                    index - 1)
    
    @next_sent.click(inputs=[dataframe,index],outputs=[dataframe,current_meaning,current_text,tf_state,choose_meaning,index])
    def next_sent_click(dataframe,index):
        if(index == len(dataframe) - 1):
            gr.Info("已到达最后一句")
            return (dataframe,
                    dataframe['meaning'][index],
                    highlight_target_word(dataframe['word'][0],dataframe['sentence'][index]),
                    gr.update(value = "是" if(dataframe['true_meaning'][index] == dataframe['meaning'][index]) else "否"),
                    gr.update(value = dataframe['true_meaning'][index]),
                    index)
        else:
            return (dataframe,
                    dataframe['meaning'][index+1],
                    highlight_target_word(dataframe['word'][0],dataframe['sentence'][index+1]),
                    gr.update(value = "是" if(dataframe['true_meaning'][index+1] == dataframe['meaning'][index+1]) else "否"),
                    gr.update(value = dataframe['true_meaning'][index+1]),
                    index + 1)
        
    @choose_meaning.input(inputs=[choose_meaning,dataframe,index],outputs=[tf_state])
    def choose_meaning_input(choose_meaning,dataframe,index):
        dataframe.loc[index,'true_meaning'] = choose_meaning
        if(choose_meaning == dataframe['meaning'][index]):
            return gr.update(value = '是')
        else:
            return gr.update(value = '否')

    @save_btn.click(inputs=[dataframe,index],outputs=[])
    def save_state(dataframe,index):
        if(isinstance(dataframe,pd.DataFrame)):
            dataframe.to_csv("./annotated_data/" + dataframe['word'][0] + ".csv",index=False)
            file_progress[dataframe['word'][0]][0] = index
            gr.Info("标注结果已保存")
        else:
            dataframe = None

if __name__ == "__main__":
    demo.launch()