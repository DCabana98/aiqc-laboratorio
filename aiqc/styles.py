# ==============================================================
# AIQC – Hoja de estilos (CSS)
# ==============================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"]{
background-color:#F4F6F9!important;color:#1C2B3A;font-family:'Inter','Segoe UI',sans-serif;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1E2D40 0%,#16202E 100%)!important;
border-right:none!important;box-shadow:4px 0 24px rgba(0,0,0,.18);}
[data-testid="stSidebar"] *{color:#CBD5E1!important;}
[data-testid="stSidebar"] strong,[data-testid="stSidebar"] b{color:#E2E8F0!important;}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.10)!important;}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]{
background:rgba(255,255,255,.05)!important;
border:1.5px dashed rgba(255,255,255,.20)!important;border-radius:10px!important;}
[data-testid="stSidebar"] [data-baseweb="select"]>div{
background:rgba(255,255,255,.08)!important;border:1px solid rgba(255,255,255,.15)!important;
border-radius:8px!important;color:#E2E8F0!important;}
[data-testid="stSidebar"] [data-testid="stDateInput"] input{
background:rgba(255,255,255,.08)!important;border:1px solid rgba(255,255,255,.15)!important;
border-radius:8px!important;color:#E2E8F0!important;}
[data-baseweb="select"]>div,[data-testid="stTextInput"] input,[data-testid="stDateInput"] input{
background-color:#FFFFFF!important;border:1.5px solid #D1D9E0!important;
border-radius:8px!important;color:#1C2B3A!important;}
.stButton>button[kind="primary"]{
background:linear-gradient(135deg,#1A6FC4 0%,#1557A0 100%)!important;
border:none!important;color:#FFFFFF!important;border-radius:8px!important;
font-weight:600!important;box-shadow:0 2px 8px rgba(26,111,196,.30)!important;}
.stButton>button[kind="primary"]:hover{
background:linear-gradient(135deg,#1557A0 0%,#0F3F78 100%)!important;transform:translateY(-1px)!important;}
.stButton>button[kind="secondary"]{
background-color:#FFFFFF!important;border:1.5px solid #1A6FC4!important;
color:#1A6FC4!important;border-radius:8px!important;font-weight:600!important;}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:#FFFFFF;border:1px solid #E2E8F0;
border-radius:12px;padding:5px 6px;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.stTabs [data-baseweb="tab"]{background:transparent!important;border:none!important;
border-radius:8px!important;color:#64748B!important;font-weight:500!important;
font-size:.875rem!important;padding:8px 18px!important;transition:all .18s!important;}
.stTabs [data-baseweb="tab"]:hover{background:#F1F5F9!important;color:#1A6FC4!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1A6FC4 0%,#0D9E6E 100%)!important;
color:#FFFFFF!important;font-weight:700!important;box-shadow:0 2px 8px rgba(26,111,196,.28)!important;}
.kpi-card{background:#FFFFFF;border:1px solid #E8EDF2;border-top:3px solid #1A6FC4;
border-radius:14px;padding:22px 20px 18px;text-align:center;
box-shadow:0 2px 12px rgba(0,0,0,.06);transition:box-shadow .22s,transform .22s;}
.kpi-card:hover{box-shadow:0 8px 28px rgba(0,0,0,.11);transform:translateY(-3px);}
.kpi-card.estado-verde{border-top-color:#0D9E6E;}
.kpi-card.estado-ambar{border-top-color:#F59E0B;}
.kpi-card.estado-rojo{border-top-color:#E53E3E;}
.kpi-val{font-size:2.1rem;font-weight:800;letter-spacing:-.6px;line-height:1.1;}
.kpi-lbl{font-size:.70rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:.10em;margin-top:8px;}
.kpi-sub{font-size:.76rem;color:#B0BAC9;margin-top:3px;}
.badge{display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:999px;
font-size:.78rem;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,.10);}
.badge-green{background:linear-gradient(135deg,#D1FAE5,#A7F3D0);color:#065F46;border:1px solid #6EE7B7;}
.badge-amber{background:linear-gradient(135deg,#FEF3C7,#FDE68A);color:#92400E;border:1px solid #FCD34D;}
.badge-red{background:linear-gradient(135deg,#FEE2E2,#FECACA);color:#991B1B;border:1px solid #FCA5A5;}
.nivel-pill{display:inline-block;padding:4px 13px;border-radius:999px;font-size:.76rem;font-weight:700;}
.nivel-N{background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;}
.nivel-PB{background:#FFFBEB;color:#92400E;border:1px solid #FDE68A;}
.nivel-PA{background:#FFF1F2;color:#9F1239;border:1px solid #FECDD3;}
.aiqc-header{background:linear-gradient(135deg,#1A6FC4 0%,#0D9E6E 100%);
border-radius:16px;padding:22px 28px;margin-bottom:12px;box-shadow:0 4px 20px rgba(26,111,196,.22);}
.aiqc-header h2{color:#FFFFFF!important;margin:0 0 4px;font-size:1.5rem;font-weight:800;}
.aiqc-header .meta{color:rgba(255,255,255,.82);font-size:.875rem;}
.quick-bar{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
padding:10px 16px;margin-bottom:16px;box-shadow:0 1px 6px rgba(0,0,0,.05);}
.sb-logo{text-align:center;font-size:2.8rem;margin-bottom:2px;}
.sb-title{text-align:center;font-size:1.2rem;font-weight:800;
background:linear-gradient(135deg,#60A5FA,#34D399);-webkit-background-clip:text;
-webkit-text-fill-color:transparent;margin-bottom:2px;}
.sb-sub{text-align:center;font-size:.75rem;color:#64748B!important;margin-bottom:16px;}
.data-pill{background:rgba(96,165,250,.12);border:1px solid rgba(96,165,250,.28);
border-radius:10px;padding:10px 14px;font-size:.82rem;color:#93C5FD!important;margin-top:8px;}
.sync-pill{background:rgba(13,158,110,.12);border:1px solid rgba(13,158,110,.30);
border-radius:10px;padding:10px 14px;font-size:.82rem;color:#34D399!important;margin-top:8px;}
.sec-head{font-size:.95rem;font-weight:700;color:#1A6FC4;border-left:3px solid #0D9E6E;
padding-left:10px;margin:26px 0 14px;}
.login-card{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:20px;padding:52px 48px;
max-width:420px;margin:60px auto 0;box-shadow:0 12px 40px rgba(0,0,0,.10);}
.gemini-banner{background:linear-gradient(135deg,#EFF6FF 0%,#ECFDF5 100%);
border:1px solid #BFDBFE;border-radius:10px;padding:10px 16px;font-size:12.5px;
color:#1E40AF;margin-bottom:14px;}
.biorad-card{background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid #1A6FC4;
border-radius:12px;padding:18px 20px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,.05);}
.biorad-card-red{background:#FFFAFA;border:1px solid #FECACA;border-left:4px solid #E53E3E;
border-radius:12px;padding:18px 20px;margin-bottom:12px;box-shadow:0 2px 12px rgba(229,62,62,.08);}
.biorad-card-amber{background:#FFFDF5;border:1px solid #FDE68A;border-left:4px solid #F59E0B;
border-radius:12px;padding:18px 20px;margin-bottom:12px;box-shadow:0 2px 12px rgba(245,158,11,.08);}
.audit-row{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;
padding:8px 14px;margin-bottom:6px;font-size:.82rem;}
.role-admin{background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;
border-radius:6px;padding:2px 8px;font-size:.72rem;font-weight:700;}
.role-supervisor{background:#F0FDF4;color:#166534;border:1px solid #BBF7D0;
border-radius:6px;padding:2px 8px;font-size:.72rem;font-weight:700;}
.role-tecnico{background:#FFFBEB;color:#92400E;border:1px solid #FDE68A;
border-radius:6px;padding:2px 8px;font-size:.72rem;font-weight:700;}
table{width:100%;border-collapse:collapse;font-size:.86rem;}
thead tr{background:#F8FAFC;}
th{padding:11px 13px;text-align:left;font-weight:700;color:#475569;
border-bottom:2px solid #E2E8F0;text-transform:uppercase;font-size:.72rem;letter-spacing:.06em;}
td{padding:10px 13px;border-bottom:1px solid #F1F5F9;color:#1C2B3A;}
tr:hover td{background:#F8FAFC;}
[data-testid="stChatMessage"]{background:#FFFFFF!important;border:1px solid #E2E8F0!important;
border-radius:14px!important;box-shadow:0 1px 4px rgba(0,0,0,.05)!important;}
[data-testid="stMetric"]{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
padding:16px 14px;box-shadow:0 2px 8px rgba(0,0,0,.05);}
[data-testid="stExpander"]{background:#FFFFFF!important;border:1px solid #E2E8F0!important;border-radius:10px!important;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:#F1F5F9;}
::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#94A3B8;}
</style>
"""
