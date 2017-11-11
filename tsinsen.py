import requests
import code
import json
import os
import re
def _getJSON(st):
    start_pos=st.find('var obj =')
    start_pos+=len('var obj =')
    end_pos=st.find('\r\n',start_pos)-1
    return [start_pos,end_pos]

class tsinsen:
    def __init__(self,username,password):
        self.headers={"Content-Type":"text/xml; charset=UTF-8"} 
        self.main_url='http://www.tsinsen.com'
        self.username=username
        self.password=password
        self.isLogin=False
        self.submit_history_loaded=False
        self.history_questions_loaded=False
        self.history_questions={}       
        self.finished_questions={}
    def login(self):
        auth_xml='<xml><pusername>%s</pusername><ppassword>%s</ppassword></xml>'%(self.username,self.password)        
        r = requests.post(self.main_url+'/user.Login.dt', data=auth_xml,headers=self.headers)
        obj=json.loads(r.text)
        if(obj['ret']=='1'):
            self.isLogin=True
            self.session=requests.Session()
            self.session.cookies=r.cookies
        else:
            print('login failed')
        return
    def submit(self,question_id):
        submit_file_name='%s.cpp'%question_id
        if not(os.path.exists(submit_file_name)):
            print(submit_file_name,' not exist!')
            return
        files = {'file': (submit_file_name,open(submit_file_name, 'rb'),'multipart/form-data')}
        r=self.session.post(self.main_url+'/CommonFileUpload.do',files=files)
        if not(r.text.find('cpp')):
            print('submit failed')
            return
        submit_file_name_on_server=re.search('([0-9_A-Za-z_-]+\.cpp)',r.text).group(1)
        #add problem specific info
        xml_data='<xml><pgpid>%s</pgpid><pcodefn>%s</pcodefn></xml>'%(question_id,submit_file_name_on_server)
        r=self.session.post(self.main_url+'/test.SubmitCode.dt', data=xml_data,headers=self.headers)
        response_json=json.loads(r.text)
        if(response_json['ret']=='1'):
            #submit successfully,add itemid to finished_questions
            #finished_questions[question_id]['sh'][response_json['itemid']]
        return
    def get_submit_id_info(self,question_id,submit_id):
        if not(self.submit_history_loaded):
            print("user submit_history_loaded...")
            self.get_history_per_question(question_id)
            if not(self.submit_history_loaded):
                return
        if(self.finished_questions.get(question_id) and self.finished_questions[question_id]['sh'].get(submit_id)):
            r=self.session.get(self.main_url+'/DetailResult.page?submitid='+submit_id)
            sp,ep=_getJSON(r.text)
            self.submit_id_info=json.loads(r.text[sp:ep])   
            f=open('output.cpp','w')
            f.write(self.submit_id_info['code'])
            f.close() #source code submitted        
        else:
            print('submit_id %s of %s not found'%(question_id,submit_id))
                
        if(self.submit_id_info['result'].find('编译')<0):#scoring result in detail
            for i in range(10):
                result_in_detail=self.submit_id_info[('d%d'%i)]
                print(i+1,result_in_detail['time'],result_in_detail['memory'],result_in_detail['score']+'score')
        else:#compiler error, if any
            print('compiler error')
        return
    def _collect_history_questions(self):
        if not(self.history_questions_loaded):
            print("user load history questions...")
            self.get_history_all_questions()
            if not(self.history_questions_loaded):
                return
        for i in ti.finished_questions.keys():
            r=ti.session.get(ti.main_url+'/'+i)
            st=r.text.replace('/styles/Tsinsen2011','./styles/Tsinsen2011')
            f=open('history_questions/%s.html'%i,'wb')
            f.write(st.encode('utf-8'))
            f.close()
    def get_history_per_question(self,question_id):
        if not(self.history_questions_loaded):
            print("user load history questions...")
            self.get_history_all_questions()
            if not(self.history_questions_loaded):
                return
        if not(self.submit_history_loaded):
            #get page_count from first request
            xml_data='<xml><puserid>-1</puserid><ppage>0</ppage></xml>'   
            r = self.session.post(self.main_url+'/test.SelectResults.dt?type=a###type=m', data=xml_data,headers=self.headers)
            obj=json.loads(r.text)
            page_num=int(obj['pagecnt'])
            for i in range(1,page_num):
                xml_data='<xml><puserid>-1</puserid><ppage>%d</ppage></xml>'%(i)   
                r = self.session.post(self.main_url+'/test.SelectResults.dt?type=a###type=m', data=xml_data,headers=self.headers)        
                obj=json.loads(r.text)            
                max_question_submit_group=self._get_max_group(obj.keys())
                for j in range(max_question_submit_group):
                    obj_inner=obj[str(j)]
                    if not(obj_inner.get('gpid')):
                        continue
                    if(self.finished_questions.get(obj_inner['gpid'])):
                        inner_pointer=self.finished_questions[obj_inner['gpid']]
                        if not(inner_pointer.get('sh')):
                            inner_pointer['sh']={}#submit history
                        inner_pointer['sh'][obj_inner['id']]={'score':obj_inner['score'],'time':obj_inner['submit']}
            self.submit_history_loaded=True            
        if(self.finished_questions.get(question_id)):
            inner_pointer=self.finished_questions[question_id]
            if not(inner_pointer.get('sh')):
                print('question %s has no submit history'%question_id)
            else:
                for key,value in inner_pointer['sh'].items():
                    print(value['time']+' : '+key+' '+value['score'])
        else:
            print('question %s not found'%question_id)
        return
    def _get_max_group(self,dic_keys):
        max_group=0
        for i in dic_keys:
            if(ord(i[0])>=48 and ord(i[0])<=57 and max_group<int(i)):
                max_group=int(i)
        return max_group+1
    def get_history_all_questions(self):
        if not(self.isLogin):
            print("user login...")
            self.login()
            if not(self.isLogin):
                return
        if not(self.history_questions):#if history_question dictionary is empty, request first from server
            r=self.session.get(self.main_url+'/MyAssignment.page')
            st=r.text
            start_pos,end_pos=_getJSON(st)
            st1=st[start_pos:end_pos]
            self.history_questions=json.loads(st1,encoding='utf-8')
        
        max_question_group_outer=self._get_max_group(self.history_questions.keys())
        for i in range(max_question_group_outer):
            obj=self.history_questions[str(i)]
            max_question_group_inner=self._get_max_group(obj.keys())            
            problem_str=''
            for j in range(max_question_group_inner):
                problem_str+=obj[str(j)]['title']+'~'+obj[str(j)]['gpid']+' '
                self.finished_questions[obj[str(j)]['gpid']]={'title':obj[str(j)]['title']}
            print(problem_str)
        self.history_questions_loaded=True
#if __name__ == "__main__":
#    tsinsen_instance=tsinsen()
