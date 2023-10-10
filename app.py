from api_entrance_point import api_entrance_point
# from robust_bias_aware.data.study_bias_scores.update_study_bias_scores import update_study_bias_scores
# from robust_bias_aware.data.networks.update_networks import update_networks
import flask
from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
import json
import pandas as pd
import json
import shortuuid
from flask_apscheduler import APScheduler
import os
import time
from jsonmerge import merge

########################## SET MODE: ############################################
mode=1 # Manually set: 0 (runtime testing) or 1 (actually running the app)
#################################################################################

app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379"

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)
####################### Links: #######################
host_url = os.environ.get('HOST', '127.0.0.1:5000')
# robust_home_url = f'http://{host_url}'
# robust_about_url = f'http://{host_url}/robust_about'
# robust_documentation_url = f'http://{host_url}/robust_documentation'
# run_robust_url = f'http://{host_url}/run_robust'

# host_url = os.environ.get('HOST', '0.0.0.0')
# robust_home_url = f'https://{host_url}'
# robust_about_url = f'https://{host_url}/robust_about'
# robust_documentation_url = f'http://{host_url}/robust_documentation'
# run_robust_url = f'https://{host_url}/run_robust'

######################################################


@celery.task()
def celery_running_task(custom_id, input_dict):
    t0=time.time()
    node_list, api_output_df, is_seed, robust_run_time = api_entrance_point(input_dict)
    nodeData = node_list
    edgeDataSrc = api_output_df['edge_list_src'].values.tolist()
    edgeDataDest = api_output_df['edge_list_dest'].values.tolist()
    nodeData_str = _convert_list_to_comma_separated_string(nodeData)
    edgeDataSrc_str = _convert_list_to_comma_separated_string(edgeDataSrc)
    edgeDataDest_str = _convert_list_to_comma_separated_string(edgeDataDest)
    is_seed_strings = [str(x) for x in is_seed]
    is_seed_str = ','.join(is_seed_strings)
    record = Robust(custom_id, input_dict["path_to_graph"], input_dict["seeds"], input_dict["namespace"],
                    input_dict["alpha"], input_dict["beta"], input_dict["n"], input_dict["tau"],
                    input_dict["study_bias_score"], input_dict["study_bias_score_data"], input_dict["gamma"],
                    input_dict["in_built_network"], input_dict["provided_network"], input_dict["is_graphml"],
                    nodeData_str, edgeDataSrc_str, edgeDataDest_str, is_seed_str, input_dict["param_str"])
    db.session.add(record)
    db.session.commit()
    t1=time.time()
    total_celery_running_task_time=t1-t0
    if mode==0:
        return robust_run_time, total_celery_running_task_time
    elif mode==1:
        return "Done!"


# Use Cron if Flask-Scheduler doesn't work well on the server:
# ------------------------------------------------------------
# cron = Scheduler(daemon=True)
# # Explicitly kick off the background thread
# cron.start()
# @cron.interval_schedule(hours=0)
# def job_function():
#     update_study_bias_data()
# # Shutdown your cron thread if the web process is stopped
# atexit.register(lambda: cron.shutdown(wait=False))

scheduler = APScheduler()


def update_study_bias_scores_scheduled_task():
    try:
        update_study_bias_scores()
        tasks=Robust.query.all()
        for task in tasks:
            if 'BAIT_USAGE' in str(task.parameter_str) or 'STUDY_ATTENTION' in str(task.parameter_str):
                task.delete()
    except:
        pass



def update_networks_scheduled_task():
    try:
        update_networks()
        tasks=Robust.query.all()
        for task in tasks:
            if 'BioGRID' in str(task.parameter_str) or 'APID' in str(task.parameter_str) or 'STRING' in str(task.parameter_str):
                task.delete()
    except:
        pass


# --------------------------------------------------------------


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/robust.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)


class Robust(db.Model):
    __tablename__ = 'robust'
    id = db.Column(db.Integer, primary_key=True)
    custom_id = db.Column(db.Integer, primary_key=False, unique=True)
    path_to_graph = db.Column(db.String)
    seeds = db.Column(db.String)
    namespace = db.Column(db.String)
    alpha = db.Column(db.Float)
    beta = db.Column(db.Float)
    n = db.Column(db.Integer, primary_key=False)
    tau = db.Column(db.Float)
    study_bias_score = db.Column(db.String)
    study_bias_score_data = db.Column(db.String)
    gamma = db.Column(db.Float)
    in_built_network = db.Column(db.String)
    provided_network = db.Column(db.String)
    is_graphml = db.Column(db.Boolean)
    nodeData_str = db.Column(db.String)
    edgeDataSrc_str = db.Column(db.String)
    edgeDataDest_str = db.Column(db.String)
    is_seed_str = db.Column(db.String)
    parameter_str=db.Column(db.String)

    def __init__(self, custom_id, path_to_graph, seeds, namespace, alpha, beta, n, tau, study_bias_score,
                 study_bias_score_data, gamma, in_built_network, provided_network, is_graphml, nodeData_str,
                 edgeDataSrc_str, edgeDataDest_str, is_seed_str, parameter_str):
        self.custom_id = custom_id
        self.path_to_graph = path_to_graph
        self.seeds = seeds
        self.namespace = namespace
        self.alpha = alpha
        self.beta = beta
        self.n = n
        self.tau = tau
        self.study_bias_score = study_bias_score
        self.study_bias_score_data = study_bias_score_data
        self.gamma = gamma
        self.in_built_network = in_built_network
        self.provided_network = provided_network
        self.is_graphml = is_graphml
        self.nodeData_str = nodeData_str
        self.edgeDataSrc_str = edgeDataSrc_str
        self.edgeDataDest_str = edgeDataDest_str
        self.is_seed_str = is_seed_str
        self.parameter_str=parameter_str


class Task_Added(db.Model):
    __tablename__ = 'task_added'
    id = db.Column(db.Integer, primary_key=True)
    custom_id = db.Column(db.Integer, primary_key=False, unique=True)

    def __init__(self, custom_id):
        self.custom_id = custom_id


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/robust_about', methods=['GET'])
def robust_about():
    return render_template('robust_about.html')


@app.route('/robust_documentation', methods=['GET'])
def robust_documentation():
    return render_template('robust_documentation.html')


@app.route('/run_robust', methods=['POST', 'GET'])
def run_robust():
    return render_template('run_robust.html')


@app.route('/check_input_data', methods=['POST', 'GET'])
def check_input_data():
    return render_template('check_input_data.html')



# @app.route('/results_viz_temp', methods=['POST'])
# def check_input_data():
#     return render_template('check_input_data.html')

# @app.route('/results_viz_temp', methods=['POST', 'GET'])
# def results_viz_temp():
#     if flask.request.method == 'POST':
#         custom_id = _generate_custom_id()
#         NETWORK, NAMESPACE, STUDY_BIAS_SCORE = _initialize_dropdown_params()
#         study_bias_score_data = 'BAIT_USAGE'
#         uploaded_network = ''
#         namespace, alpha, beta, n, tau, study_bias_score, gamma, path_to_graph, uploaded_network, seeds = _initialize_input_params(
#             NETWORK, NAMESPACE, STUDY_BIAS_SCORE)
#         # return str(uploaded_network)
#         is_graphml = False
#         in_built_network = request.form.get("network_selection")
#         ppi_network_contents_df = pd.DataFrame()
#         provided_network, ppi_network_contents_df, is_graphml = _get_network_contents(is_graphml, in_built_network,
#                                                                                       ppi_network_contents_df,
#                                                                                       uploaded_network, NETWORK)
#         custom_studybiasdata_input_df = pd.DataFrame()
#         study_bias_score_data, custom_studybiasdata_input_df = _get_study_bias_data_contents(
#             custom_studybiasdata_input_df, study_bias_score)
#         error_statement = _empty_seeds_error(seeds)
#         if not error_statement == 'None':
#             return render_template('run_robust.html', error=error_statement)
#         # return(str(ppi_network_contents_df))
#         ppi_network_contents_df, error_statement = _network_error(in_built_network, is_graphml, ppi_network_contents_df)
#         if not error_statement == 'None':
#             return render_template('run_robust.html', error=error_statement)
#         custom_studybiasdata_input_df, error_statement = _custom_study_bias_data_error(study_bias_score,
#                                                                                        custom_studybiasdata_input_df)
#         if not error_statement == 'None':
#             return render_template('run_robust.html', error=error_statement)
        
#         seeds_list=split_seeds(seeds)
#         seeds_list_alphabetical=arrange_alphabetical(seeds_list)
#         seeds_str_alphabetical=list_to_str(seeds_list_alphabetical)

#         if path_to_graph in ['BioGRID', 'APID', 'STRING'] and study_bias_score in ['No', 'BAIT_USAGE', 'STUDY_ATTENTION']:
#             param_str=path_to_graph+seeds_str_alphabetical+namespace+str(alpha)+str(beta)+str(n)+str(n)+str(tau)+str(study_bias_score)+str(gamma)
#             found_added_task = _is_saved_results(param_str)
#             # # if not found_added_task==0:
#                 # # # return found_added_task
#                 # # return redirect(f'/saved_results/{found_added_task}')

#         input_dict = _make_input_dict(path_to_graph, seeds, namespace, alpha, beta, n, tau, study_bias_score,
#                                       study_bias_score_data, gamma, in_built_network, provided_network, is_graphml, param_str)
#         if mode==1:
#             celery_running_task.delay(custom_id, input_dict)
#             record_taskAdded = Task_Added(custom_id)
#             db.session.add(record_taskAdded)
#             db.session.commit()
#             return render_template('running_celery_task.html', custom_id=custom_id)
#         elif mode==0:
#             robust_run_time, total_celery_running_task_time=celery_running_task(custom_id, input_dict)
#             return str(robust_run_time) 
#     else:
#         return render_template('results_get_error.html')



# @app.route('/run_enquire_temp', methods=['POST', 'GET'])
# def run_enquire_temp():
#     return render_template('run_enquire_temp.html')


def _initialize_dropdown_params_visualizations():
    param1 = ['Option-1', 'Option-2', 'Option-3', 'Option-4']
    return param1

def _initialize_input_params_visualizations(PARAMETER1):
    node_data=''
    edge_data=''
    edge_literature_data=''
    
    try:
        param1 = PARAMETER1[int(request.form.get("param1"))]  # dropdown list
    except:
        param1 = 'Option-1'
    try:
        alpha = float(request.form.get('alpha'))  # number field
    except:
        alpha = 0.25
    try:
        beta = float(request.form.get('beta'))  # number field
    except:
        beta = 0.9
    try:
        gamma = int(request.form.get('gamma'))  # number field
    except:
        gamma = 30
    try:
        delta = float(request.form.get('delta'))  # number field
    except:
        delta = 0.1
    try:
        tau = float(request.form.get('delta'))  # number field
    except:
        tau = 0.1
    
    ###############################################################
    
    filepath_nodes=''
    filepath_edges=''
    filepath_lit=''

    # get the uploaded file
    try:
        uploaded_file_nodes = request.files['inputfile_nodes']
    except:
        uploaded_file_nodes=''
    try:
        uploaded_file_edges = request.files['inputfile_edges']
    except:
        uploaded_file_edges = ''
    try:
        uploaded_file_lit = request.files['inputfile_lit']
    except:
        uploaded_file_lit=''

    if uploaded_file_nodes.filename!='' and uploaded_file_edges.filename!='' and uploaded_file_lit.filename!='':
        filepath_nodes = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_nodes.filename)
        uploaded_file_nodes.save(filepath_nodes)
        # ---------------------------------------
        filepath_edges = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_edges.filename)
        uploaded_file_edges.save(filepath_edges)
        # ---------------------------------------
        filepath_lit = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_lit.filename)
        uploaded_file_lit.save(filepath_lit)
    return param1, alpha, beta, gamma, delta, tau, filepath_nodes, uploaded_file_nodes.filename, filepath_edges, uploaded_file_edges.filename, filepath_lit, uploaded_file_lit.filename

    ###############################################################

###############################################################
def preprocess_node_data_in_robust_output_subnetwork(G):
    node_list=[]
    is_seed=[]
    for i, data in G.nodes(data=True):
        node_list.append(i)
        if data['isSeed']:
            is_seed.append(int(1))
        else:
            is_seed.append(int(0))
    return node_list, is_seed

def preprocess_edge_data_in_robust_output_subnetwork(G):
    _edges=list(G.edges)
    edge_list_src=[]
    edge_list_dest=[]
    edge_data=[]
    for i,j in _edges:
        edge_list_src.append(i)
        edge_list_dest.append(j)
        edge_dict = {"from": i, "to": j, "group": "default"}
        edge_data.append(edge_dict)
    output_data_df=pd.DataFrame()
    output_data_df['edge_list_src'] = pd.Series(edge_list_src)
    output_data_df['edge_list_dest'] = pd.Series(edge_list_dest)
    return output_data_df
#'''''''''''''''''''''''''''''''''''
def _make_dict(node_data, edge_data):
    outputData_dict = {"nodes": node_data, "edges": edge_data}
    return outputData_dict
def _convert_dict_to_json(outputData_dict):
    OutputData_json = json.dumps(outputData_dict)
    return OutputData_json
###############################################################

# @app.route('/results_viz_temp', methods=['POST', 'GET'])
# def results_viz_temp():

#     new_filepath_nodes = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_node_data')
#     new_filepath_edges = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_edge_data')
#     new_filepath_lit = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_lit_data')

#     node_data=pd.read_csv(new_filepath_nodes, sep='\t')
#     edge_data=pd.read_csv(new_filepath_edges, sep='\t')
#     lit_data=pd.read_csv(new_filepath_lit, sep='\t')

#     node_list=[]
#     node_list_final=[]

#     list_of_nodes=[]
    
#     gene_color='#E8544E'
#     mesh_color='#FFD265'

#     ##########return node_data.columns[1]

#     # jsondata = {}
#     # agent={}
#     # content={}
#     # agent['agentid'] = 'john'
#     # content['eventType'] = 'view'
#     # content['othervar'] = "new"

#     # jsondata['agent'] = agent
#     # jsondata['content'] = content
#     # print(json.dumps(jsondata))
        
#     for index, row in node_data.iterrows():
#         # jsondata = {}

#         # id_data={}
        
#         # # marker_data={}
#         # # radius_data={}

#         # color_data={}




#         list_of_nodes.append(str(row['Node']))

#         rad=float(row['Wscore'])*50
        
        
#         if str(row['Category'])=='GENE':
#             # return "gene!"
#             # id_data['id']=str(row['Node'])
#             # color_data['color']=gene_color


#             # node_list_final.append(merge(id_data, color_data))
            
            


#             data = {
#                 "id": str(row['Node']),
#                 "marker": {
#                     "radius": float(rad)},
#                 "color": '#E8544E'
#                 }
            
#             data_json=json.dumps(data)
#             data_json=json.loads(data_json)
#             node_list.append(data_json)

# # print(json.dumps(data))

            
            
            
            
            
            
#             # '{ "name":"John", "age":30, "city":"New York"}'


#             # node_list.append(f'{"id": str(row["Node"]), "marker":{"radius": float(row["Wscore"])},"color": "#E8544E"}')
        
#         elif str(row['Category'])=='MESH':
#             # return "mesh!"
#             data = {
#                 "id": str(row['Node']),
#                 "marker": {
#                     "radius": float(rad)},
#                 "color": '#FFD265'
#                 }
            
#             data_json=json.dumps(data)
#             data_json=json.loads(data_json)
#             node_list.append(data_json)
#             # id_data['id']=str(row['Node'])
#             # color_data['color']=gene_color


#             # node_list_final.append(merge(id_data, color_data))


#             # node_list.append(
#             #     {'id': str(row['Node']),
#             #     'marker':{
#             #         'radius': float(row['Wscore'])
#             #         },
#             #     'color': '#FFD265'
#             #     })
#     list_of_nodes=list(set(list_of_nodes))
#     # node_data_dict = {"nodes": node_list}
#     # node_data_json = json.dumps(node_data_dict)

#     # return str(node_list_final)

#     # return type(node_list).__name__

#     #####print(type(some_object).__name__)


#     edge_list=[]
#     for index, row in edge_data.iterrows():
#         if str(row['Node1']) in list_of_nodes and str(row['Node2']) in list_of_nodes:
#             edge_list.append([str(row['Node1']), str(row['Node2'])])
    
#     # return edge_list[0][1]
    
    
#     return render_template('results_viz_temp.html', node_list=node_list, edge_list=edge_list, list_of_nodes=list_of_nodes)






    # node_params_mandatory=set(['Node', 'Category'])
    # node_params_optional=set(['Representativeness', 'Raw_occurrence', 'Betweenness_centrality', 'Closeness_centrality', 'Strength', 'Wscore', 'Knode', 'Knode_rank', 'Community_membership'])
    # # -----------------------------------------------
    # edge_params_mandatory=set(['Node1', 'Node2'])
    # edge_params_optional=set(['P_value', 'Adj_p_value', 'Fisher_p_value', 'zt_pois_cdf', 'Raw_co_occurrence', 'Expansion'])
    # # -----------------------------------------------
    # lit_params_mandatory=set(['Node1', 'Node2', 'link'])
        
        
        # print(row['c1'], row['c2'])
        # Node	Category	Representativeness	Raw_occurrence	Betweenness_centrality	Closeness_centrality	Strength	Wscore	Knode	Knode_rank	Community_membership




    # return str(node_data.columns[0])
    



    # data_=[['node1', 'node2'], ['node2', 'node3']]
    # return render_template('results_viz_temp.html', data_=data_)
    # # return render_template('results_viz_temp.html')

@app.route('/run_enquire_temp2', methods=['POST'])
def run_enquire_temp2():
    custom_id = _generate_custom_id()
    PARAMETER1=_initialize_dropdown_params_visualizations()
    param1, alpha, beta, gamma, delta, tau, filepath_nodes, filename_nodes, filepath_edges, filename_edges, filepath_lit, filename_lit = _initialize_input_params_visualizations(PARAMETER1)
    error_results_viz_temp='0'
    if flask.request.method == 'POST':
        if filename_nodes=='' or filename_edges=='' or filename_lit=='':
            if filename_nodes=='':
                error_results_viz_temp='1.0.(nodes)'
                return render_template('empty_data_path_error.html', error_results_viz_temp=error_results_viz_temp)
            if filename_edges=='':
                error_results_viz_temp='1.0.(edges)'
                return render_template('empty_data_path_error.html', error_results_viz_temp=error_results_viz_temp)
            if filename_lit=='':
                error_results_viz_temp='1.0.(lit)'
                return render_template('empty_data_path_error.html', error_results_viz_temp=error_results_viz_temp)
        # return filename_nodes
        else:
            if filename_nodes.endswith('csv'):
                sep_nodes=','
            elif filename_nodes.endswith('tsv'):
                sep_nodes='\t'
            elif filename_nodes.endswith('txt'):
                sep_nodes=' '
            else:
                error_results_viz_temp='fileFormatIncorrect'
                fileFormatIncorrect='nodes'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, fileFormatIncorrect=fileFormatIncorrect, data_uploaded=data_uploaded)
                return render_template('incorrect_file_format_error.html', error_results_viz_temp=error_results_viz_temp, fileFormatIncorrect=fileFormatIncorrect, error_filename=filename_nodes)
            try:
                nodes_df=pd.read_csv(filepath_nodes, sep=sep_nodes)
            except:
                error_results_viz_temp='fileFormatIncorrect'
                fileFormatIncorrect='nodes'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, fileFormatIncorrect=fileFormatIncorrect, data_uploaded=data_uploaded)
                return render_template('incorrect_file_format_error.html', error_results_viz_temp=error_results_viz_temp, fileFormatIncorrect=fileFormatIncorrect, error_filename=filename_nodes)
            # -------------------------------------------      
            if filename_edges.endswith('csv'):
                sep_edges=','
            elif filename_edges.endswith('tsv'):
                sep_edges='\t'
            elif filename_edges.endswith('txt'):
                sep_edges=' '
            else:
                error_results_viz_temp='fileFormatIncorrect'
                fileFormatIncorrect='edges'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, fileFormatIncorrect=fileFormatIncorrect, data_uploaded=data_uploaded)
                return render_template('incorrect_file_format_error.html', error_results_viz_temp=error_results_viz_temp, fileFormatIncorrect=fileFormatIncorrect, error_filename=filename_edges)
            try:
                edges_df=pd.read_csv(filepath_edges, sep=sep_edges)
            except:
                error_results_viz_temp='fileFormatIncorrect'
                fileFormatIncorrect='edges'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, fileFormatIncorrect=fileFormatIncorrect, data_uploaded=data_uploaded)
                return render_template('incorrect_file_format_error.html', error_results_viz_temp=error_results_viz_temp, fileFormatIncorrect=fileFormatIncorrect, error_filename=filename_edges)
            # -------------------------------------------
            if filename_lit.endswith('csv'):
                sep_lit=','
            elif filename_lit.endswith('tsv'):
                sep_lit='\t'
            elif filename_lit.endswith('txt'):
                sep_lit=' '
            else:
                error_results_viz_temp='fileFormatIncorrect'
                fileFormatIncorrect='lit'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, fileFormatIncorrect=fileFormatIncorrect, data_uploaded=data_uploaded)
                return render_template('incorrect_file_format_error.html', error_results_viz_temp=error_results_viz_temp, fileFormatIncorrect=fileFormatIncorrect, error_filename=filename_lit)
            try:
                lit_df=pd.read_csv(filepath_lit, sep=sep_lit)
            except:
                error_results_viz_temp='fileFormatIncorrect'
                fileFormatIncorrect='lit'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, fileFormatIncorrect=fileFormatIncorrect, data_uploaded=data_uploaded)
                return render_template('incorrect_file_format_error.html', error_results_viz_temp=error_results_viz_temp, fileFormatIncorrect=fileFormatIncorrect, error_filename=filename_lit)
            error_run_scAnalyzer='notEnoughRows'
            not_enough_data='nodes'
            # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, data_uploaded=data_uploaded)
            # return render_template('insufficient_data_error.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, error_filename=filename_nodes)
            # =======================================================================================================
            if nodes_df.shape[0] <= 1:
                error_run_scAnalyzer='notEnoughRows'
                not_enough_data='nodes'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, data_uploaded=data_uploaded)
                return render_template('insufficient_data_error.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, error_filename=filename_nodes)
            if nodes_df.shape[1] <= 2:
                error_run_scAnalyzer='notEnoughColumns'
                not_enough_data='nodes'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, data_uploaded=data_uploaded)
                return render_template('insufficient_data_error.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, error_filename=filename_nodes)
            # -------------------------------------------
            if edges_df.shape[0] <= 1:
                error_run_scAnalyzer='notEnoughRows'
                not_enough_data='edges'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, data_uploaded=data_uploaded)
                return render_template('insufficient_data_error.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, error_filename=filename_edges)
            if edges_df.shape[1] <= 2:
                error_run_scAnalyzer='notEnoughColumns'
                not_enough_data='edges'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, data_uploaded=data_uploaded)
                return render_template('insufficient_data_error.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, error_filename=filename_edges)
            # -------------------------------------------
            if lit_df.shape[0] <= 1:
                error_run_scAnalyzer='notEnoughRows'
                not_enough_data='lit'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, data_uploaded=data_uploaded)
                return render_template('insufficient_data_error.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, error_filename=filename_lit)
            if lit_df.shape[1] <= 3:
                error_run_scAnalyzer='notEnoughColumns'
                not_enough_data='lit'
                # return render_template('index.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, data_uploaded=data_uploaded)
                return render_template('insufficient_data_error.html', error_run_scAnalyzer=error_run_scAnalyzer, not_enough_data=not_enough_data, error_filename=filename_lit)
            # -------------------------------------------
            new_filepath_nodes = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_node_data')
            new_filepath_edges = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_edge_data')
            new_filepath_lit = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_lit_data')
            os.rename(filepath_nodes, new_filepath_nodes)
            os.rename(filepath_edges, new_filepath_edges)
            os.rename(filepath_lit, new_filepath_lit)
            nodes_df=pd.read_csv(new_filepath_nodes, sep=sep_nodes)
            edges_df=pd.read_csv(new_filepath_edges, sep=sep_edges)
            lit_df=pd.read_csv(new_filepath_lit, sep=sep_lit)
            # -------------------------------------------
            # node_param_list, edge_param_list, lit_param_list = _check_params(nodes_df, edges_df, lit_df)
            error_flag_input_data, node_params_list, edge_params_list, lit_params_list=_check_params(nodes_df, edges_df, lit_df)
            if error_flag_input_data==0:
                nodes_df___Representativeness=nodes_df[['Node', 'Category', 'Representativeness']]
                nodes_df___Representativeness_sorted=nodes_df___Representativeness.sort_values('Representativeness', ascending=False)
                barchartList_Representativeness=[]
                barchartList_Representativeness_categories=[]
                barchartList_Representativeness_data=[]
                
                colors_Representativeness=[]

                count=0
                gene_color='#ff0000'
                mesh_color='#00ff00'
                for index, row in nodes_df___Representativeness_sorted.iterrows():
                    count+=1
                    if (count>20):
                        break
                    barchartList_Representativeness.append([str(row['Node']), float(row['Representativeness'])])
                    barchartList_Representativeness_categories.append(str(row['Node']))
                    barchartList_Representativeness_data.append(float(row['Representativeness']))
                    if row['Category']=='GENE':
                        colors_Representativeness.append(gene_color)
                    elif row['Category']=='MESH':
                        colors_Representativeness.append(mesh_color)
                # --------------------------------------------------------------------------------
                # nodes_df___RawOccurrence=nodes_df[['Node', 'Category', 'Raw_occurrence']]
                # nodes_df___RawOccurrence_sorted=nodes_df___RawOccurrence.sort_values('Raw_occurrence', ascending=False)
                # barchartList_RawOccurrence=[]
                # colors_RawOccurrence=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df___RawOccurrence_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_RawOccurrence.append([str(row['Node']), float(row['Raw_occurrence'])])
                #     if row['Category']=='GENE':
                #         colors_RawOccurrence.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_RawOccurrence.append(mesh_color)
                # # --------------------------------------------------------------------------------
                # nodes_df___BetweennessCentrality=nodes_df[['Node', 'Category', 'Betweenness_centrality']]
                # nodes_df___BetweennessCentrality_sorted=nodes_df___BetweennessCentrality.sort_values('Betweenness_centrality', ascending=False)
                # barchartList_BetweennessCentrality=[]
                # colors_BetweennessCentrality=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df___BetweennessCentrality_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_BetweennessCentrality.append([str(row['Node']), float(row['Betweenness_centrality'])])
                #     if row['Category']=='GENE':
                #         colors_BetweennessCentrality.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_BetweennessCentrality.append(mesh_color)
                # # --------------------------------------------------------------------------------
                # nodes_df___ClosenessCentrality=nodes_df[['Node', 'Category', 'Closeness_centrality']]
                # nodes_df___ClosenessCentrality_sorted=nodes_df___ClosenessCentrality.sort_values('Closeness_centrality', ascending=False)
                # barchartList_ClosenessCentrality=[]
                # colors_ClosenessCentrality=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df___ClosenessCentrality_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_ClosenessCentrality.append([str(row['Node']), float(row['Closeness_centrality'])])
                #     if row['Category']=='GENE':
                #         colors_ClosenessCentrality.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_ClosenessCentrality.append(mesh_color)
                # # --------------------------------------------------------------------------------
                # nodes_df___Strength=nodes_df[['Node', 'Category', 'Strength']]
                # nodes_df___Strength_sorted=nodes_df___Strength.sort_values('Strength', ascending=False)
                # barchartList_Strength=[]
                # colors_Strength=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df___Strength_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_Strength.append([str(row['Node']), float(row['Strength'])])
                #     if row['Category']=='GENE':
                #         colors_Strength.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_Strength.append(mesh_color)
                # # --------------------------------------------------------------------------------
                # nodes_df___Wscore=nodes_df[['Node', 'Category', 'Wscore']]
                # nodes_df___Wscore_sorted=nodes_df___Wscore.sort_values('Wscore', ascending=False)
                # barchartList_Wscore=[]
                # colors_Wscore=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df___Wscore_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_Wscore.append([str(row['Node']), float(row['Wscore'])])
                #     if row['Category']=='GENE':
                #         colors_Wscore.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_Wscore.append(mesh_color)
                # # --------------------------------------------------------------------------------
                # nodes_df___Knode=nodes_df[['Node', 'Category', 'Knode']]

                # nodes_df__Knode_sorted=nodes_df___Knode.sort_values('Knode', ascending=False)
                # barchartList_Knode=[]
                # colors_Knode=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df__Knode_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_Knode.append([str(row['Node']), float(row['Knode'])])
                #     if row['Category']=='GENE':
                #         colors_Knode.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_Knode.append(mesh_color)
                # # --------------------------------------------------------------------------------
                # nodes_df___KnodeRank=nodes_df[['Node', 'Category', 'Knode_rank']]
                # nodes_df__KnodeRank_sorted=nodes_df___KnodeRank.sort_values('Knode_rank', ascending=False)
                # barchartList_KnodeRank=[]
                # colors_KnodeRank=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df__KnodeRank_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_KnodeRank.append([str(row['Node']), float(row['Knode_rank'])])
                #     if row['Category']=='GENE':
                #         colors_KnodeRank.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_KnodeRank.append(mesh_color)
                # # --------------------------------------------------------------------------------
                # nodes_df___CommunityMembership=nodes_df[['Node', 'Category', 'Community_membership']]
                # nodes_df__CommunityMembership_sorted=nodes_df___CommunityMembership.sort_values('Community_membership', ascending=False)
                # barchartList_CommunityMembership=[]
                # colors_CommunityMembership=[]
                # count=0
                # gene_color='#ff0000'
                # mesh_color='#00ff00'
                # for index, row in nodes_df__CommunityMembership_sorted.iterrows():
                #     count+=1
                #     if (count>20):
                #         break
                #     barchartList_CommunityMembership.append([str(row['Node']), float(row['Community_membership'])])
                #     if row['Category']=='GENE':
                #         colors_CommunityMembership.append(gene_color)
                #     elif row['Category']=='MESH':
                #         colors_CommunityMembership.append(mesh_color)
                # # --------------------------------------------------------------------------------
                    
                # return type(barchartList_Representativeness[0][0])
                # return type(barchartList_Representativeness[0][0]).__name__
                # return colors_Representativeness[4]
                
                
                
                # # Sort by Ascending
                # df2 = df.sort_values('Courses')
                # # Sort by Descending
                # df2 = df.sort_values('Courses', ascending=False)
                # # Sort by multiple columns
                # df2 = df.sort_values(by=['Courses','Fee'])

                # return barchartList_Representativeness[19][0]

                # ######################################################################################################################################################

                node_data=pd.read_csv(new_filepath_nodes, sep='\t')
                edge_data=pd.read_csv(new_filepath_edges, sep='\t')
                lit_data=pd.read_csv(new_filepath_lit, sep='\t')

                node_list=[]
                node_list_final=[]

                list_of_nodes=[]
                
                gene_color='#E8544E'
                mesh_color='#FFD265'

                _list_of_nodes_=[]
                for index, row in node_data.iterrows():
                    _list_of_nodes_.append(str(row['Node']))
                _list_of_nodes_=list(set(_list_of_nodes_))

                dict_expansion_color={0: 'red', 1: 'yellow', 2: 'blue', 3: 'green', 4: 'purple', 5: 'orange', 6: 'pink'}
                edge_list=[]
                list_of_nodes_in_edge_list=[]
                for index, row in edge_data.iterrows():
                    if str(row['Node1']) in  _list_of_nodes_ and str(row['Node2']) in  _list_of_nodes_:
                        list_of_nodes_in_edge_list.append(str(row['Node1']))
                        list_of_nodes_in_edge_list.append(str(row['Node2']))
                        # ---------------------------------------------------
                        lit_data_df=lit_data.loc[(lit_data['Node1'] == str(row['Node1'])) & (lit_data['Node2'] == str(row['Node2']))]
                        lit_data_df_link=lit_data_df['link'].tolist()
                        lit_data_df_QuerySet=lit_data_df['QuerySet'].tolist()

                        lit_data_df2=lit_data.loc[(lit_data['Node1'] == str(row['Node2'])) & (lit_data['Node2'] == str(row['Node1']))]
                        lit_data_df2_link=lit_data_df2['link'].tolist()
                        lit_data_df2_QuerySet=lit_data_df2['QuerySet'].tolist()

                        lit_data_df_link=list(set(lit_data_df_link).union(set(lit_data_df2_link)))
                        lit_data_df_QuerySet=list(set(lit_data_df_QuerySet).union(set(lit_data_df2_QuerySet)))
                        # ---------------------------------------------------
                        # # RESPONSE WITHOUT EDGE_LITERATURE_DATA:
                        # edge_list.append([str(row['Node1']), str(row['Node2']), dict_expansion_color[row['Expansion']]])
                        # # RESPONSE WITH EDGE_LITERATURE_DATA:
                        # # Variation-1:
                        # lit_data_df_link='\n'.join(lit_data_df_link)
                        # lit_data_df_QuerySet='\n'.join(lit_data_df_QuerySet)
                        # edge_list.append([str(row['Node1']), str(row['Node2']), dict_expansion_color[row['Expansion']], lit_data_df_link, lit_data_df_QuerySet])
                        # # Variation-2:
                        edge_list.append([str(row['Node1']), str(row['Node2']), dict_expansion_color[row['Expansion']], lit_data_df_link, lit_data_df_QuerySet])
                list_of_nodes_in_edge_list=list(set(list_of_nodes_in_edge_list))

                ###############################################################################################################
                    
                for index, row in node_data.iterrows():

                    if str(row['Node']) in list_of_nodes_in_edge_list:

                        list_of_nodes.append(str(row['Node']))

                        rad=float(row['Wscore'])*10
                        
                        
                        if str(row['Category'])=='GENE':
                            
                            data = {
                                "id": str(row['Node']),
                                "marker": {
                                    "radius": float(rad)},
                                "color": '#E8544E'
                                }
                            
                            data_json=json.dumps(data)
                            data_json=json.loads(data_json)
                            node_list.append(data_json)

                        
                        elif str(row['Category'])=='MESH':
                            
                            data = {
                                "id": str(row['Node']),
                                "marker": {
                                    "radius": float(rad)},
                                "color": '#FFD265'
                                }
                            
                            data_json=json.dumps(data)
                            data_json=json.loads(data_json)
                            node_list.append(data_json)
                        
                list_of_nodes=list(set(list_of_nodes))
                

                #******************************************************************#
                # list_of_nodes=list(set(list_of_nodes).intersection(set(list_of_nodes_in_edge_list)))
                #******************************************************************#
                
                

                # ######################################################################################################################################################

                return render_template('results_viz_temp.html', barchartList_Representativeness=barchartList_Representativeness, colors_Representativeness=colors_Representativeness, barchartList_Representativeness_data=barchartList_Representativeness_data, barchartList_Representativeness_categories=barchartList_Representativeness_categories, node_list=node_list, edge_list=edge_list, list_of_nodes=list_of_nodes)
            else:
                if error_flag_input_data=='1.(nodes)':
                    return render_template('input_error_page_missing_columns.html', error_flag_input_data=error_flag_input_data, node_params_list=node_params_list, error_filename=filename_nodes)
                elif error_flag_input_data=='1.(edges)':
                    return render_template('input_error_page_missing_columns.html', error_flag_input_data=error_flag_input_data, edge_params_list=edge_params_list, error_filename=filename_edges)
                elif error_flag_input_data=='1.(lit)':
                    return render_template('input_error_page_missing_columns.html', error_flag_input_data=error_flag_input_data, lit_params_list=lit_params_list, error_filename=filename_lit)
    
    # # # return render_template('empty_data_path_error.html')




@app.route('/results_node_characteristics', methods=['POST'])
def results_node_characteristics():
    new_filepath_nodes = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_node_data')
    new_filepath_edges = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_edge_data')
    new_filepath_lit = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_lit_data')

    sep_nodes="\t"
    sep_edges="\t"
    sep_lit="\t"
    #-------------------------------------------------------------------------
    nodes_df=pd.read_csv(new_filepath_nodes, sep=sep_nodes)
    edges_df=pd.read_csv(new_filepath_edges, sep=sep_edges)
    lit_df=pd.read_csv(new_filepath_lit, sep=sep_lit)
    #-------------------------------------------------------------------------
    nodes_df___Representativeness=nodes_df[['Node', 'Category', 'Representativeness']]
    nodes_df___Representativeness_sorted=nodes_df___Representativeness.sort_values('Representativeness', ascending=False)
    barchartList_Representativeness=[]
    barchartList_Representativeness_categories=[]
    barchartList_Representativeness_data=[]
    #-------------------------------------------------------------------------           
    colors_Representativeness=[]
    #-------------------------------------------------------------------------
    count=0
    gene_color='#ff0000'
    mesh_color='#00ff00'
    for index, row in nodes_df___Representativeness_sorted.iterrows():
        count+=1
        if (count>20):
            break
        barchartList_Representativeness.append([str(row['Node']), float(row['Representativeness'])])
        barchartList_Representativeness_categories.append(str(row['Node']))
        barchartList_Representativeness_data.append(float(row['Representativeness']))
        if row['Category']=='GENE':
            colors_Representativeness.append(gene_color)
        elif row['Category']=='MESH':
            colors_Representativeness.append(mesh_color)
    return render_template('results_node_characteristics.html', barchartList_Representativeness=barchartList_Representativeness, colors_Representativeness=colors_Representativeness, barchartList_Representativeness_data=barchartList_Representativeness_data, barchartList_Representativeness_categories=barchartList_Representativeness_categories)



def _check_params(nodes_df, edges_df, lit_df):
    node_columns=set(nodes_df.columns)
    edge_columns=set(edges_df.columns)
    lit_columns=set(lit_df.columns)
    # -----------------------------------------------
    node_params_mandatory=set(['Node', 'Category'])
    node_params_optional=set(['Representativeness', 'Raw_occurrence', 'Betweenness_centrality', 'Closeness_centrality', 'Strength', 'Wscore', 'Knode', 'Knode_rank', 'Community_membership'])
    # -----------------------------------------------
    edge_params_mandatory=set(['Node1', 'Node2'])
    edge_params_optional=set(['P_value', 'Adj_p_value', 'Fisher_p_value', 'zt_pois_cdf', 'Raw_co_occurrence', 'Expansion'])
    # -----------------------------------------------
    lit_params_mandatory=set(['Node1', 'Node2', 'link'])
    # -----------------------------------------------
    if node_params_mandatory.issubset(node_columns) and edge_params_mandatory.issubset(edge_columns) and lit_params_mandatory.issubset(lit_columns):
        error_flag=0
        node_params_list=[]
        edge_params_list=[]
        lit_params_list=''
        for node in node_params_optional:
            if node in list(node_columns):
                node_params_list.append(1)
            else:
                node_params_list.append(0)
        for edge in edge_params_optional:
            if edge in list(edge_columns):
                edge_params_list.append(1)
            else:
                edge_params_list.append(0)
    else:
        node_params_list=''
        edge_params_list=''
        lit_params_list=''
        if not node_params_mandatory.issubset(node_columns):
            error_flag='1.(nodes)'
            node_params_list+='| '
            for node in node_params_mandatory:
                if not(node in list(node_columns)):
                    node_params_list=node_params_list+' '+str(node)+' |'
            # return 1, 'node_error', ''
        if not edge_params_mandatory.issubset(edge_columns):
            error_flag='1.(edges)'
            edge_params_list+='| '
            for edge in edge_params_mandatory:
                if not(edge in list(edge_columns)):
                    edge_params_list=edge_params_list+' '+str(edge)+' |'
        
        if not lit_params_mandatory.issubset(lit_columns):
            error_flag='1.(lit)'
            lit_params_list+='| '
            for lit_ in lit_params_mandatory:
                if not(lit_ in list(lit_columns)):
                    lit_params_list=lit_params_list+' '+str(lit_)+' |'
    return error_flag, node_params_list, edge_params_list, lit_params_list


@app.route('/results', methods=['POST', 'GET'])
def results():
    if flask.request.method == 'POST':
        custom_id = _generate_custom_id()
        NETWORK, NAMESPACE, STUDY_BIAS_SCORE = _initialize_dropdown_params()
        study_bias_score_data = 'BAIT_USAGE'
        uploaded_network = ''
        namespace, alpha, beta, n, tau, study_bias_score, gamma, path_to_graph, uploaded_network, seeds = _initialize_input_params(
            NETWORK, NAMESPACE, STUDY_BIAS_SCORE)
        # return str(uploaded_network)
        is_graphml = False
        in_built_network = request.form.get("network_selection")
        ppi_network_contents_df = pd.DataFrame()
        provided_network, ppi_network_contents_df, is_graphml = _get_network_contents(is_graphml, in_built_network,
                                                                                      ppi_network_contents_df,
                                                                                      uploaded_network, NETWORK)
        custom_studybiasdata_input_df = pd.DataFrame()
        study_bias_score_data, custom_studybiasdata_input_df = _get_study_bias_data_contents(
            custom_studybiasdata_input_df, study_bias_score)
        error_statement = _empty_seeds_error(seeds)
        if not error_statement == 'None':
            return render_template('run_robust.html', error=error_statement)
        # return(str(ppi_network_contents_df))
        ppi_network_contents_df, error_statement = _network_error(in_built_network, is_graphml, ppi_network_contents_df)
        if not error_statement == 'None':
            return render_template('run_robust.html', error=error_statement)
        custom_studybiasdata_input_df, error_statement = _custom_study_bias_data_error(study_bias_score,
                                                                                       custom_studybiasdata_input_df)
        if not error_statement == 'None':
            return render_template('run_robust.html', error=error_statement)
        
        seeds_list=split_seeds(seeds)
        seeds_list_alphabetical=arrange_alphabetical(seeds_list)
        seeds_str_alphabetical=list_to_str(seeds_list_alphabetical)

        if path_to_graph in ['BioGRID', 'APID', 'STRING'] and study_bias_score in ['No', 'BAIT_USAGE', 'STUDY_ATTENTION']:
            param_str=path_to_graph+seeds_str_alphabetical+namespace+str(alpha)+str(beta)+str(n)+str(n)+str(tau)+str(study_bias_score)+str(gamma)
            found_added_task = _is_saved_results(param_str)
            # # if not found_added_task==0:
                # # # return found_added_task
                # # return redirect(f'/saved_results/{found_added_task}')

        input_dict = _make_input_dict(path_to_graph, seeds, namespace, alpha, beta, n, tau, study_bias_score,
                                      study_bias_score_data, gamma, in_built_network, provided_network, is_graphml, param_str)
        if mode==1:
            celery_running_task.delay(custom_id, input_dict)
            record_taskAdded = Task_Added(custom_id)
            db.session.add(record_taskAdded)
            db.session.commit()
            return render_template('running_celery_task.html', custom_id=custom_id)
        elif mode==0:
            robust_run_time, total_celery_running_task_time=celery_running_task(custom_id, input_dict)
            return str(robust_run_time)
    else:
        return render_template('results_get_error.html')

def list_to_str(list_):
    str_ =" ".join(str(item) for item in list_)
    return str_


def split_seeds(seeds):
    seeds_=str(seeds)
    seeds_ = seeds_.split()
    # print(seeds_)
    return seeds_

def arrange_alphabetical(seeds_list):
    seeds_list.sort()
    return seeds_list

@app.route('/saved_results/<int:saved_id>', methods=['POST', 'GET'])
def retrieve(saved_id):
    found_added_task = _is_added_task(saved_id)
    if found_added_task == 1:
        found_done_task = 0
        done_tasks = Robust.query.all()
        for done_task in done_tasks:
            if str(done_task.custom_id) == str(saved_id):
                retrievedRecord = Robust.query.get(done_task.id)
                found_done_task = 1
        if found_done_task == 1:
            custom_id, path_to_graph, seeds, namespace, alpha, beta, n, tau, study_bias_score, study_bias_score_data, gamma, in_built_network, provided_network, is_graphml, nodeData_str, edgeDataSrc_str, edgeDataDest_str, is_seed_str, parameter_str = query_Robust_database(
                retrievedRecord)
            input_network = _check_input_network(provided_network)
            if nodeData_str == "":
                return render_template('empty_output_returned.html', retrievedRecord=retrievedRecord,
                                       input_network=input_network)
            input_dict = _make_input_dict(path_to_graph, seeds, namespace, alpha, beta, n, tau, study_bias_score,
                                          study_bias_score_data, gamma, in_built_network, provided_network, is_graphml, parameter_str)
            _nodes = _convert_comma_separated_str_to_list(nodeData_str)
            src = _convert_comma_separated_str_to_list(edgeDataSrc_str)
            dest = _convert_comma_separated_str_to_list(edgeDataDest_str)
            _edges = zip(src, dest)
            _is_seed = _convert_comma_separated_str_to_list(is_seed_str)
            is_seed_int = _convert_strList_to_intList(_is_seed)
            node_data = _make_node_data(_nodes, is_seed_int)
            edge_data = _make_edge_data(_edges)
            outputData_dict = _make_dict(node_data, edge_data)
            OutputData_json = _convert_dict_to_json(outputData_dict)
            accessLink = _make_access_link(custom_id)
            input_seeds = _split_data_to_list(seeds)
            return render_template('saved_results.html', retrievedRecord=retrievedRecord, input_dict=input_dict,
                                   OutputData_json=OutputData_json, namespace=namespace, accessLink=accessLink,
                                   input_network=input_network, input_seeds=input_seeds, n=n)
        else:
            return render_template('running_celery_task.html', custom_id=saved_id)
    else:
        return render_template('no_such_task_exists.html', custom_id=saved_id)


def _initialize_input_params(NETWORK, NAMESPACE, STUDY_BIAS_SCORE):
    try:
        namespace = NAMESPACE[int(request.form.get("namespace"))]  # dropdown list
    except:
        namespace = 'GENE_SYMBOL'
    try:
        alpha = float(request.form.get('alpha'))  # number field
    except:
        alpha = 0.25
    try:
        beta = float(request.form.get('beta'))  # number field
    except:
        beta = 0.9
    try:
        n = int(request.form.get('n'))  # number field
    except:
        n = 30
    try:
        tau = float(request.form.get('tau'))  # number field
    except:
        tau = 0.1
    try:
        study_bias_score = STUDY_BIAS_SCORE[int(request.form.get("study_bias_score"))]  # dropdown list
    except:
        study_bias_score = 'BAIT_USAGE'
    try:
        gamma = float(request.form.get('gamma'))  # number field
    except:
        gamma = 1.0
    try:
        path_to_graph = NETWORK[int(request.form.get('inbuilt_network_selection'))]  # number field
    except:
        path_to_graph = 'BioGRID'
    try:
        uploaded_network = str(request.form.get("uploaded_ppi_network_filename"))
    except:
        pass
    seeds = ''
    try:
        seeds = request.form.get("textbox_seeds")
    except:
        pass
    return namespace, alpha, beta, n, tau, study_bias_score, gamma, path_to_graph, uploaded_network, seeds


def _convert_list_to_comma_separated_string(_list):
    _str = ','.join(_list)
    return _str


def query_Robust_database(retrievedRecord):
    custom_id = retrievedRecord.custom_id
    path_to_graph = retrievedRecord.path_to_graph
    seeds = retrievedRecord.seeds
    namespace = retrievedRecord.namespace
    alpha = retrievedRecord.alpha
    beta = retrievedRecord.beta
    n = retrievedRecord.n
    tau = retrievedRecord.tau
    study_bias_score = retrievedRecord.study_bias_score
    study_bias_score_data = retrievedRecord.study_bias_score_data
    gamma = retrievedRecord.gamma
    in_built_network = retrievedRecord.in_built_network
    provided_network = retrievedRecord.provided_network
    is_graphml = retrievedRecord.is_graphml
    nodeData_str = retrievedRecord.nodeData_str
    edgeDataSrc_str = retrievedRecord.edgeDataSrc_str
    edgeDataDest_str = retrievedRecord.edgeDataDest_str
    is_seed_str = retrievedRecord.is_seed_str
    parameter_str = retrievedRecord.parameter_str
    return custom_id, path_to_graph, seeds, namespace, alpha, beta, n, tau, study_bias_score, study_bias_score_data, gamma, in_built_network, provided_network, is_graphml, nodeData_str, edgeDataSrc_str, edgeDataDest_str, is_seed_str, parameter_str

def _is_saved_results(param_str):
    found_saved_task=0
    saved_tasks=Robust.query.all()
    for saved_task in saved_tasks:
        if str(saved_task.parameter_str)==str(param_str):
            found_saved_task=saved_task.custom_id
    return found_saved_task

def _is_added_task(saved_id):
    found_added_task = 0
    added_tasks = Task_Added.query.all()
    for added_task in added_tasks:
        if str(added_task.custom_id) == str(saved_id):
            # retrievedRecord_addedTask = Task_Added.query.get(added_task.id)
            found_added_task = 1
    return found_added_task


def _get_network_contents(is_graphml, in_built_network, ppi_network_contents_df, uploaded_network, NETWORK):
    if in_built_network == "Yes":
        try:
            provided_network = NETWORK[int(request.form.get("inbuilt_network_selection"))]
        except:
            provided_network = 'BioGRID'
    elif in_built_network == "No":
        if not uploaded_network.endswith('.graphml'):
            try:
                provided_network = request.form.get("network_contents")
                data2 = list(map(lambda x: x.split(' '), provided_network.split("\r\n")))
                ppi_network_contents_df = pd.DataFrame(data2[1:], columns=data2[0])
            except:
                pass
        elif uploaded_network.endswith('.graphml'):
            is_graphml = True
            try:
                provided_network = request.form.get("network_contents")
                data2 = list(map(lambda x: x.split(' '), provided_network.split("\r\n")))
                ppi_network_contents_df = pd.DataFrame(data2[1:], columns=data2[0])
            except:
                pass
    return provided_network, ppi_network_contents_df, is_graphml


def _make_input_dict(path_to_graph, seeds, namespace, alpha, beta, n, tau, study_bias_score, study_bias_score_data,
                     gamma, in_built_network, provided_network, is_graphml, param_str):
    input_dict = {
        "path_to_graph": path_to_graph,
        "seeds": seeds,
        "namespace": namespace,
        "alpha": alpha,
        "beta": beta,
        "n": n,
        "tau": tau,
        "study_bias_score": study_bias_score,
        "study_bias_score_data": study_bias_score_data,
        "gamma": gamma,
        "in_built_network": in_built_network,
        "provided_network": provided_network,
        "is_graphml": is_graphml,
        "param_str": param_str
    }
    return input_dict


def _custom_study_bias_data_error(study_bias_score, custom_studybiasdata_input_df):
    if study_bias_score == 'CUSTOM':
        if custom_studybiasdata_input_df.empty:
            error_statement = 'Custom study bias data has to be uploaded!'
        else:
            numRows_df = custom_studybiasdata_input_df.shape[0]
            if numRows_df == 0:
                error_statement = 'Custom study bias data with zero rows uploaded. Please add atleast one row excluding the column headers.'
            else:
                if custom_studybiasdata_input_df.shape[1] < 2:
                    error_statement = 'Custom study bias data with less than two columns uploaded. Please add two columns.'
                elif custom_studybiasdata_input_df.shape[1] >= 2:
                    custom_studybiasdata_input_df = custom_studybiasdata_input_df.iloc[:, :2]
                    error_statement = 'None'
    else:
        error_statement = 'None'
    return custom_studybiasdata_input_df, error_statement


def _network_error(in_built_network, is_graphml, ppi_network_contents_df):
    if in_built_network == "No":
        if not is_graphml == True:
            if ppi_network_contents_df.empty:
                error_statement = 'Custom network has to be uploaded!'
            else:
                numRows_df2 = ppi_network_contents_df.shape[0]
                if numRows_df2 == 0:
                    error_statement = 'Custom network with zero rows uploaded. Please add atleast one row excluding the column headers.'
                else:
                    if ppi_network_contents_df.shape[1] < 2:
                        error_statement = 'Custom network with less than two columns uploaded. Please add two columns.'
                    elif ppi_network_contents_df.shape[1] >= 2:
                        # Custom network with more than two columns uploaded. First two columns retained:
                        ppi_network_contents_df = ppi_network_contents_df.iloc[:, :2]
                        error_statement = 'None'
        else:
            error_statement = 'None'
    else:
        error_statement = 'None'
    return ppi_network_contents_df, error_statement


def _empty_seeds_error(seeds):
    if seeds == '' or seeds == None:
        error_statement = 'Seeds cannot be empty'
    else:
        error_statement = 'None'
    return error_statement


def _get_study_bias_data_contents(custom_studybiasdata_input_df, study_bias_score):
    if study_bias_score == 'CUSTOM':
        try:
            study_bias_score_data = request.form.get("custom_studybiasdata_contents_textbox")
            data = list(map(lambda x: x.split(' '), study_bias_score_data.split("\r\n")))
            custom_studybiasdata_input_df = pd.DataFrame(data[1:], columns=data[0])
        except:
            pass
    else:
        study_bias_score_data = study_bias_score
    return study_bias_score_data, custom_studybiasdata_input_df


def _initialize_dropdown_params():
    network = ['BioGRID', 'APID', 'STRING']
    namespace = ['GENE_SYMBOL', 'ENTREZ', 'ENSEMBL', 'UNIPROT']
    study_bias_score = ['No', 'BAIT_USAGE', 'STUDY_ATTENTION', 'CUSTOM']
    return network, namespace, study_bias_score


def _generate_custom_id():
    s = shortuuid.ShortUUID(alphabet="0123456789")
    custom_id = s.random(length=5)
    return custom_id


def _convert_strList_to_intList(str_list):
    intList = []
    for i in str_list:
        intList.append(int(i))
    return intList


def _convert_comma_separated_str_to_list(str_data):
    list_data = str_data.split(",")
    return list_data


def _make_node_data(_nodes, is_seed_int):
    node_data = []
    for i in range(len(_nodes)):
        if is_seed_int[i] == 1:
            node_dict = {"id": _nodes[i], "group": "important"}
        else:
            node_dict = {"id": _nodes[i], "group": "gene"}
        node_data.append(node_dict)
    return node_data


def _make_edge_data(_edges):
    edge_data = []
    for i, j in _edges:
        edge_dict = {"from": i, "to": j, "group": "default"}
        edge_data.append(edge_dict)
    return edge_data


def _make_dict(node_data, edge_data):
    outputData_dict = {"nodes": node_data, "edges": edge_data}
    return outputData_dict


def _convert_dict_to_json(outputData_dict):
    OutputData_json = json.dumps(outputData_dict)
    return OutputData_json


def _make_access_link(id):
    accessLink = f'{host_url}/saved_results/' + str(id)
    # accessLink='127.0.0.1:5000/saved_results/'+str(id)
    return accessLink


def _check_input_network(provided_network):
    if provided_network in ['BioGRID', 'APID', 'STRING']:
        input_network = provided_network
    else:
        input_network = 'custom'
    return input_network


def _split_data_to_list(data):
    str_data = str(data)
    list_data = str_data.split()
    return list_data


if __name__ == '__main__':
    scheduler.add_job(id='Updation of study bias scores', func=update_study_bias_scores_scheduled_task,
                      trigger="interval", seconds=30000)
    scheduler.add_job(id='Updation of networks', func=update_networks_scheduled_task, trigger="interval", seconds=30000)
    scheduler.start()
    db.create_all()
    app.run(debug=os.environ.get('DEBUG', '1') == '1', host='0.0.0.0')
