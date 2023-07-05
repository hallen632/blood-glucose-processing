import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import copy
#new_patient_blood_glucose_30min_before输入早中晚，餐前采样值的加总除2，new_patient_blood_glucose_steady_state输入睡前的采样值（
new_patient_blood_glucose_30min_before=[6.3,7.8,7.0]
new_patient_blood_glucose_steady_state=[]

#定义需要的静态变量
j=0
k=0
result=0

for i in new_patient_blood_glucose_30min_before:
    print(i)
    result+=i
    j+=1
    if j>=3:
        j=0
        result=result/3
        print("平均值为：",result)
        new_patient_blood_glucose_steady_state.append(result)
        k+=1
        result=0
        print("本组数据打印完成！")

for i in new_patient_blood_glucose_steady_state:
    print(i)

print(new_patient_blood_glucose_steady_state[0])
# print(new_patient_blood_glucose_steady_state[1])

print('血糖稳态值为：',new_patient_blood_glucose_steady_state)
morning_noon_evening=[7,10,11,14,16,20]
def start_matching(morning_max_time,noon_max_time,evening_max_time):
    df=pd.read_csv('Bingo_YAPEI_1229_22_34.csv',header=0,encoding='gbk')#读取已有的CGM
    print('已有CGM的行数为',df.shape[0])
    df_new=pd.DataFrame(columns=['时间','葡萄糖历史记录（mmol/L）'])#存储新生成的CGM
    morning_period=[]
    morning_period_time=[]
    noon_period=[]
    noon_period_time=[]
    evening_period=[]
    evening_period_time=[]
    current_day=df.loc[0,'时间'].split(' ')[0]
    A_nomral_max_occur=get_normalvalue(df)

    #计数单位,用以计量日期数
    day=0
    for row in range(df.shape[0]):
        date=df.loc[row,'时间'].split(' ')[0]
        hour=int(df.loc[row,'时间'].split(' ')[1].split(':')[0])
        if date==current_day:
            #print('same day')
            if hour>=morning_noon_evening[0]and hour<=morning_noon_evening[1]:
                morning_period.append(df.loc[row,'葡萄糖历史记录（mmol/L）'])
                morning_period_time.append(df.loc[row,'时间'])
            elif hour>=morning_noon_evening[2] and hour<=morning_noon_evening[3]:
                noon_period.append(df.loc[row,'葡萄糖历史记录（mmol/L）'])
                noon_period_time.append(df.loc[row,'时间'])
            else:
                evening_period.append(df.loc[row,'葡萄糖历史记录（mmol/L）'])
                evening_period_time.append(df.loc[row,'时间'])
        else:
            print('another day')
            print('新CGm的行数为',df_new.shape[0])
            #对前一天的数据做处理
            df_new=process_blood_glucose_data(morning_period,morning_period_time,noon_period,noon_period_time,evening_period,evening_period_time,morning_max_time,noon_max_time,evening_max_time,df_new,A_nomral_max_occur,day)
            if day<(len(new_patient_blood_glucose_steady_state)-1):
                day+=1
            # print(df_new['葡萄糖历史记录（mmol/L）'])
            #数据清零
            morning_period=[]
            noon_period=[]
            evening_period=[]
            current_day=date
            print(current_day)
            #获取新一天的第一个数据
            if hour>=morning_noon_evening[0] and hour<=morning_noon_evening[1]:
                morning_period.append(df.loc[row,'葡萄糖历史记录（mmol/L）'])
            elif hour>=morning_noon_evening[2] and hour<=morning_noon_evening[3]:
                noon_period.append(df.loc[row,'葡萄糖历史记录（mmol/L）'])
            else:
                evening_period.append(df.loc[row,'葡萄糖历史记录（mmol/L）'])

    #在for循环结束后还需要处理最后一次
    # df_new=Get_blood_glucose_date(morning_period, noon_period, evening_period, df_new, new_patient_blood_glucose_steady_state,A_nomral_max_occur)
    df_new=process_blood_glucose_data(morning_period,morning_period_time,noon_period,noon_period_time,evening_period,evening_period_time,morning_max_time,noon_max_time,evening_max_time,df_new,A_nomral_max_occur,day)

    print('新CGm的行数为',df_new.shape[0])
    df_new['时间']=df['时间']
    print(df_new)
    df_new.to_excel('NEW_CGM.xlsx')
    plot(df,df_new)

# def Get_blood_glucose_date(morning_period,noon_period,evening_period,df_new,new_patient_blood_glucose_steady_state,A_nomral_max_occur):
#     df_new_rows = df_new.shape[0]
#     for index in range(len(morning_period)):
#         if A_nomral_max_occur > 0:  # 只有每一个时期对应峰值的30mi_late值存在才做除法操作
#             df_new.loc[df_new_rows + index, '葡萄糖历史记录（mmol/L）'] = round(
#                 morning_period[index] * new_patient_blood_glucose_steady_state / A_nomral_max_occur,1)  # 保留一位小数
#         else:
#             df_new.loc[df_new_rows + index, '葡萄糖历史记录（mmol/L）'] = morning_period[index]
#
#     df_new_rows = df_new.shape[0]
#     for index in range(len(noon_period)):
#         if A_nomral_max_occur > 0:
#             df_new.loc[df_new_rows + index, '葡萄糖历史记录（mmol/L）'] = round(
#                 noon_period[index] * new_patient_blood_glucose_steady_state / A_nomral_max_occur, 1)
#         else:
#             df_new.loc[df_new_rows + index, '葡萄糖历史记录（mmol/L）'] = noon_period[index]
#
#     df_new_rows = df_new.shape[0]
#     for index in range(len(evening_period)):
#         if A_nomral_max_occur > 0:
#             df_new.loc[df_new_rows + index, '葡萄糖历史记录（mmol/L）'] = round(
#                 evening_period[index] * new_patient_blood_glucose_steady_state / A_nomral_max_occur, 1)
#         else:
#             df_new.loc[df_new_rows + index, '葡萄糖历史记录（mmol/L）'] = evening_period[index]

def process_blood_glucose_data(morning_period,morning_period_time,noon_period,noon_period_time,evening_period,evening_period_time,morning_max_time,noon_max_time,evening_max_time,df_new,A_nomral_max_occur,day):
    if len(morning_period)>0:
        offset_flag=False#偏移方向
        offset_num=0
        morning_period_max=max(morning_period)
        morning_period_max_index=morning_period.index(morning_period_max)
        if morning_max_time>=morning_noon_evening[0]and morning_max_time<=morning_noon_evening[1]:
            current_time_str=morning_period_time[morning_period_max_index].split(' ')[1].split(':')
            current_time=int(current_time_str[0])*60+int(current_time_str[1])
            if morning_max_time*60>=current_time:
                offset_flag=True#向后偏移
                offset_num=math.ceil((morning_max_time*60-current_time)/15)
            else:
                offset_flag=False#向前偏移
                offset_num=math.ceil((current_time-morning_max_time*60)/15)

        morning_period_temp=copy.deepcopy(morning_period)
        for index in range(len(morning_period_temp)):
            if offset_flag:#向后偏移
                if index<offset_num:
                    if morning_period_temp[index]<7.2:
                        morning_period[index]=morning_period_temp[index]
                    else:
                        morning_period[index]=7
                else:
                    #！修改为使用插值法
                    morning_period[index]=morning_period_temp[index-offset_num]
            else:#向前偏移
                if index<len(morning_period_temp)-offset_num:
                    morning_period[index]=morning_period_temp[index+offset_num]
                else:
                    #！修改为使用插值法
                    if morning_period_temp[index] < 7.2:
                        morning_period[index] = morning_period_temp[index]
                    else:
                        morning_period[index] = 7

    if len(noon_period)>0:
        offset_flag=False#偏移方向
        offset_num=0
        noon_period_max=max(noon_period)
        noon_period_max_index=noon_period.index(noon_period_max)
        if noon_max_time>=morning_noon_evening[2]and noon_max_time<=morning_noon_evening[3]:
            current_time_str=noon_period_time[noon_period_max_index].split(' ')[1].split(':')
            current_time=int(current_time_str[0])*60+int(current_time_str[1])
            if noon_max_time*60>=current_time:
                offset_flag=True#向后偏移
                offset_num=math.ceil((noon_max_time*60-current_time)/15)
            else:
                offset_flag=False#向前偏移
                offset_num=math.ceil((current_time-noon_max_time*60)/15)

        noon_period_temp=copy.deepcopy(noon_period)
        #result_1=len(noon_period_temp)
        #print("数据长度为",result_1)
        for index in range(len(noon_period_temp)):
            if offset_flag:#向后偏移
                if index<offset_num:
                    # ！修改为使用插值法
                    if noon_period_temp[index] < 7.2:
                        noon_period[index] = noon_period_temp[index]
                    else:
                        noon_period[index] = 7
                else:
                    noon_period[index]=noon_period_temp[index-offset_num]
            else:#向前偏移
                if index<len(noon_period_temp)-offset_num:
                    noon_period[index]=noon_period_temp[index+offset_num]
                else:
                    # ！修改为使用插值法
                    if noon_period_temp[index] < 7.2:
                        noon_period[index] = noon_period_temp[index]
                    else:
                        noon_period[index] = 7
            
    if len(evening_period)>0:
        offset_flag=False#偏移方向
        offset_num=0
        evening_period_max=max(evening_period)
        evening_period_max_index=evening_period.index(evening_period_max)
        if evening_max_time>=morning_noon_evening[4]and evening_max_time<=morning_noon_evening[5]:
            current_time_str=evening_period_time[evening_period_max_index].split(' ')[1].split(':')
            current_time=int(current_time_str[0])*60+int(current_time_str[1])
            if evening_max_time*60>=current_time:
                offset_flag=True#向后偏移
                offset_num=math.ceil((evening_max_time*60-current_time)/15)
            else:
                offset_flag=False#向前偏移
                offset_num=math.ceil((current_time-evening_max_time*60)/15)

        evening_period_temp=copy.deepcopy(evening_period)
        for index in range(len(evening_period_temp)):
            if offset_flag:#向后偏移
                if index<offset_num:

                    # ！修改为使用插值法
                    if evening_period_temp[index] < 7.2:
                        evening_period[index] = evening_period_temp[index]
                    else:
                        evening_period[index] = 7
                else:
                    evening_period[index]=evening_period_temp[index-offset_num]
            else:#向前偏移
                if index<len(evening_period_temp)-offset_num:
                    evening_period[index]=evening_period_temp[index+offset_num]
                else:
                    # ！修改为使用插值法
                    if evening_period_temp[index] < 7.2:
                        evening_period[index] = evening_period_temp[index]
                    else:
                        evening_period[index] = 7

    df_new_rows=df_new.shape[0]#更新df_new的行数
    for index in range(len(morning_period)):
        df_new.loc[df_new_rows+index,'葡萄糖历史记录（mmol/L）']=round(morning_period[index]*new_patient_blood_glucose_steady_state[day]/A_nomral_max_occur,1)#保留一位小数


    df_new_rows=df_new.shape[0]
    for index in range(len(noon_period)):
        df_new.loc[df_new_rows+index,'葡萄糖历史记录（mmol/L）']=round(noon_period[index]*new_patient_blood_glucose_steady_state[day]/A_nomral_max_occur,1)
    

    df_new_rows=df_new.shape[0]
    for index in range(len(evening_period)):
        df_new.loc[df_new_rows+index,'葡萄糖历史记录（mmol/L）']=round(evening_period[index]*new_patient_blood_glucose_steady_state[day]/A_nomral_max_occur,1)

    return df_new

def plot(df,df_new):
    x_ticks=[]
    x_label=[]
    for index in range(9):
            x_ticks.append(int(((df.shape[0]-1)/8)*index))
            x_label.append(df.loc[int(((df.shape[0]-1)/8)*index),'时间'])

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(12, 8))
    plt.title('Blood glucose date',fontsize=12)
    plt.ylabel("mmol/L")
    plt.xlabel("Time")
    plt.xticks(x_ticks,x_label,fontsize=8)
    plt.plot(df['葡萄糖历史记录（mmol/L）'],'g',linestyle = "-",linewidth = "1",label='Orignal CGM')
    plt.plot(df_new['葡萄糖历史记录（mmol/L）'],'darkorange',linestyle = "-",linewidth = "1",label='New CGM')
    plt.legend(loc='best')
    plt.show()

def get_normalvalue(df):
    value_counts=df['葡萄糖历史记录（mmol/L）'].value_counts()
    print(value_counts)
    A_nomral_max_occur=value_counts.keys()[0]
    print('平稳时间出现次数最多的值',A_nomral_max_occur)
    return A_nomral_max_occur



if __name__ == '__main__':
    start_matching(9,12.5,18.5)