//+------------------------------------------------------------------+
//|                                       smc_ai_dashboard.mq5      |
//|                          SMC AI WinWorld — Python Bridge Panel   |
//|                                                                  |
//|  Lit le fichier smc_ai_signal.txt écrit par Python live_loop.py |
//|  et affiche un panel + lignes Entry/SL/TP directement sur le    |
//|  graphique MT5.                                                  |
//|                                                                  |
//|  Installation:                                                   |
//|    1. Copier ce fichier dans :                                   |
//|       MT5 → Fichier → Ouvrir le dossier des données →           |
//|       MQL5 / Experts /                                           |
//|    2. Compiler (F7) dans MetaEditor                              |
//|    3. Glisser l'EA sur le graphique EURUSD.s H4                 |
//+------------------------------------------------------------------+
#property copyright   "SMC AI WinWorld"
#property version     "1.00"
#property description "Affiche les signaux SMC AI depuis le bridge Python"
#property strict

//── Paramètres ────────────────────────────────────────────────────────────────
input int    InpRefresh   = 10;                    // Rafraîchissement (secondes)
input string InpFile      = "smc_ai_signal.txt";   // Fichier signal (MQL5/Files/)
input int    InpPanelX    = 15;                    // Position X du panel
input int    InpPanelY    = 25;                    // Position Y du panel
input bool   InpShowLines = true;                  // Afficher lignes Entry/SL/TP

//── Couleurs ──────────────────────────────────────────────────────────────────
#define CLR_BG      C'22,27,34'
#define CLR_BORDER  C'48,54,61'
#define CLR_TEXT    C'230,237,243'
#define CLR_MUTED   C'139,148,158'
#define CLR_GREEN   C'63,185,80'
#define CLR_RED     C'248,81,73'
#define CLR_BLUE    C'88,166,255'
#define CLR_ORANGE  C'240,136,62'
#define CLR_YELLOW  C'210,153,34'

//── Variables globales ────────────────────────────────────────────────────────
string g_symbol        = "";
string g_d1_bias       = "";
bool   g_idm           = false;
string g_active_schema = "none";
string g_direction     = "none";
double g_entry         = 0;
double g_sl            = 0;
double g_tp            = 0;
string g_schema        = "none";
string g_status        = "WAITING";
string g_timestamp     = "";
bool   g_has_signal    = false;

//+------------------------------------------------------------------+
int OnInit()
  {
   EventSetTimer(InpRefresh);
   _ReadSignal();
   _DrawAll();
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   EventKillTimer();
   _DeleteAll();
  }

//+------------------------------------------------------------------+
void OnTimer()
  {
   _ReadSignal();
   _DrawAll();
  }

//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam,
                  const double &dparam, const string &sparam)
  {
   if(id == CHARTEVENT_CHART_CHANGE)
      _DrawAll();
  }

//+------------------------------------------------------------------+
//  Lecture du fichier signal
//+------------------------------------------------------------------+
void _ReadSignal()
  {
   int handle = FileOpen(InpFile, FILE_READ | FILE_TXT | FILE_ANSI);
   if(handle == INVALID_HANDLE)
     {
      g_status = "OFFLINE";
      g_has_signal = false;
      return;
     }

   // Reset
   g_symbol = ""; g_d1_bias = ""; g_idm = false;
   g_active_schema = "none"; g_direction = "none";
   g_entry = 0; g_sl = 0; g_tp = 0;
   g_schema = "none"; g_status = "WAITING";
   g_timestamp = ""; g_has_signal = false;

   while(!FileIsEnding(handle))
     {
      string line = FileReadString(handle);
      string parts[];
      if(StringSplit(line, '=', parts) < 2)
         continue;

      string key = parts[0];
      string val = parts[1];

      if(key == "SYMBOL")        g_symbol        = val;
      if(key == "D1_BIAS")       g_d1_bias       = val;
      if(key == "IDM_CONFIRMED") g_idm           = (val == "true");
      if(key == "ACTIVE_SCHEMA") g_active_schema = val;
      if(key == "DIRECTION")     g_direction     = val;
      if(key == "ENTRY")         g_entry         = StringToDouble(val);
      if(key == "SL")            g_sl            = StringToDouble(val);
      if(key == "TP")            g_tp            = StringToDouble(val);
      if(key == "SCHEMA")        g_schema        = val;
      if(key == "STATUS")        g_status        = val;
      if(key == "TIMESTAMP")     g_timestamp     = val;
     }
   FileClose(handle);

   g_has_signal = (g_status == "SIGNAL"
                   && g_direction != "none"
                   && g_direction != ""
                   && g_entry > 0);
  }

//+------------------------------------------------------------------+
//  Dessin principal
//+------------------------------------------------------------------+
void _DrawAll()
  {
   _DeleteAll();

   int panelW = 290;
   int panelH = g_has_signal ? 250 : 170;
   int x = InpPanelX;
   int y = InpPanelY;

   // Fond du panel
   _Rect("smc_bg", x, y, panelW, panelH, CLR_BG, CLR_BORDER);

   int tx = x + 14;
   int ty = y + 12;

   // ── Titre ────────────────────────────────────────────────────────────────
   _Lbl("smc_title", "⚡ SMC AI WinWorld", tx, ty, CLR_BLUE, 12, true);
   ty += 22;
   _Lbl("smc_sep0", _Line(36), tx, ty, CLR_BORDER, 9, false);
   ty += 13;

   // ── D1 Bias ──────────────────────────────────────────────────────────────
   color biasClr;
   string biasStr;
   if(g_d1_bias == "bullish")
     { biasClr = CLR_GREEN;  biasStr = "▲ BULLISH"; }
   else if(g_d1_bias == "bearish")
     { biasClr = CLR_RED;    biasStr = "▼ BEARISH"; }
   else
     { biasClr = CLR_MUTED;  biasStr = "—  Inconnu"; }

   _Lbl("smc_bias_l", "D1 Bias",       tx,      ty, CLR_MUTED, 10, false);
   _Lbl("smc_bias_v", biasStr,         tx + 95, ty, biasClr,   10, true);
   ty += 18;

   // ── IDM ──────────────────────────────────────────────────────────────────
   color idmClr  = g_idm ? CLR_GREEN : CLR_RED;
   string idmStr = g_idm ? "✓  Confirmé" : "✗  Non confirmé";
   _Lbl("smc_idm_l", "IDM",            tx,      ty, CLR_MUTED, 10, false);
   _Lbl("smc_idm_v", idmStr,           tx + 95, ty, idmClr,    10, false);
   ty += 18;

   // ── Schéma actif ─────────────────────────────────────────────────────────
   string schStr;
   color  schClr;
   if(g_active_schema == "none" || g_active_schema == "")
     { schStr = "—  Pas de setup";  schClr = CLR_MUTED; }
   else if(g_active_schema == "a1")
     { schStr = "A1  (OB/FVG+IDM)"; schClr = CLR_BLUE; }
   else if(g_active_schema == "b4")
     { schStr = "B4  (IFC Extreme)"; schClr = CLR_ORANGE; }
   else if(g_active_schema == "b2")
     { schStr = "B2  (IFC IDM)";     schClr = CLR_YELLOW; }
   else
     { schStr = g_active_schema;     schClr = CLR_BLUE; }

   _Lbl("smc_sch_l", "Schéma",         tx,      ty, CLR_MUTED, 10, false);
   _Lbl("smc_sch_v", schStr,           tx + 95, ty, schClr,    10, true);
   ty += 18;

   // ── Statut Python ────────────────────────────────────────────────────────
   color stClr;
   string stStr;
   if(g_status == "SIGNAL")
     { stClr = CLR_GREEN;  stStr = "● SIGNAL ACTIF"; }
   else if(g_status == "WAITING")
     { stClr = CLR_MUTED;  stStr = "○ En attente…"; }
   else
     { stClr = CLR_RED;    stStr = "✗ HORS LIGNE"; }
   _Lbl("smc_st_l",  "Statut",         tx,      ty, CLR_MUTED, 10, false);
   _Lbl("smc_st_v",  stStr,            tx + 95, ty, stClr,     10, true);
   ty += 18;

   // ── Timestamp ────────────────────────────────────────────────────────────
   string tsShow = g_timestamp != "" ? g_timestamp : "—";
   _Lbl("smc_ts_l",  "Mise à jour",    tx,      ty, CLR_MUTED, 9,  false);
   _Lbl("smc_ts_v",  tsShow,           tx + 95, ty, CLR_MUTED, 9,  false);
   ty += 16;

   if(!g_has_signal)
     {
      ChartRedraw();
      return;
     }

   // ── Signal ───────────────────────────────────────────────────────────────
   _Lbl("smc_sep1", _Line(36),         tx,      ty, CLR_BORDER, 9, false);
   ty += 13;

   color  dirClr = (g_direction == "buy") ? CLR_GREEN : CLR_RED;
   string dirTxt = (g_direction == "buy") ? "▲  BUY" : "▼  SELL";
   _Lbl("smc_dir",  dirTxt,            tx,      ty, dirClr,    14, true);
   ty += 24;

   _Lbl("smc_e_l",  "Entrée",          tx,      ty, CLR_MUTED, 10, false);
   _Lbl("smc_e_v",  DoubleToString(g_entry, _Digits), tx + 95, ty, CLR_TEXT,  10, true);
   ty += 17;

   _Lbl("smc_sl_l", "Stop Loss",       tx,      ty, CLR_MUTED, 10, false);
   _Lbl("smc_sl_v", DoubleToString(g_sl, _Digits),   tx + 95, ty, CLR_RED,   10, true);
   ty += 17;

   _Lbl("smc_tp_l", "Take Profit",     tx,      ty, CLR_MUTED, 10, false);
   _Lbl("smc_tp_v", DoubleToString(g_tp, _Digits),   tx + 95, ty, CLR_GREEN, 10, true);

   // ── Lignes horizontales sur le graphique ─────────────────────────────────
   if(InpShowLines)
     {
      _HLine("smc_line_e",  g_entry, CLR_BLUE,  STYLE_DASH,    1, "▶ Entry");
      _HLine("smc_line_sl", g_sl,    CLR_RED,   STYLE_DASHDOT, 1, "✗ SL");
      _HLine("smc_line_tp", g_tp,    CLR_GREEN, STYLE_DASHDOT, 1, "✓ TP");
     }

   ChartRedraw();
  }

//+------------------------------------------------------------------+
//  Helpers
//+------------------------------------------------------------------+
void _Lbl(string name, string text,
          int x, int y, color clr, int fs, bool bold)
  {
   if(ObjectFind(0, name) < 0)
      ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_CORNER,    CORNER_LEFT_UPPER);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, name, OBJPROP_COLOR,     clr);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE,  fs);
   ObjectSetString(0,  name, OBJPROP_FONT,      bold ? "Arial Bold" : "Arial");
   ObjectSetString(0,  name, OBJPROP_TEXT,      text);
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0, name, OBJPROP_BACK,      false);
   ObjectSetInteger(0, name, OBJPROP_HIDDEN,    true);
  }

void _Rect(string name, int x, int y, int w, int h, color bg, color border)
  {
   if(ObjectFind(0, name) < 0)
      ObjectCreate(0, name, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_CORNER,       CORNER_LEFT_UPPER);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE,    x);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE,    y);
   ObjectSetInteger(0, name, OBJPROP_XSIZE,        w);
   ObjectSetInteger(0, name, OBJPROP_YSIZE,        h);
   ObjectSetInteger(0, name, OBJPROP_BGCOLOR,      bg);
   ObjectSetInteger(0, name, OBJPROP_BORDER_COLOR, border);
   ObjectSetInteger(0, name, OBJPROP_BORDER_TYPE,  BORDER_FLAT);
   ObjectSetInteger(0, name, OBJPROP_BACK,         true);
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE,   false);
   ObjectSetInteger(0, name, OBJPROP_HIDDEN,        true);
  }

void _HLine(string name, double price, color clr,
            ENUM_LINE_STYLE style, int width, string label)
  {
   if(ObjectFind(0, name) < 0)
      ObjectCreate(0, name, OBJ_HLINE, 0, 0, price);
   ObjectSetDouble(0,  name, OBJPROP_PRICE,      price);
   ObjectSetInteger(0, name, OBJPROP_COLOR,      clr);
   ObjectSetInteger(0, name, OBJPROP_STYLE,      style);
   ObjectSetInteger(0, name, OBJPROP_WIDTH,      width);
   ObjectSetString(0,  name, OBJPROP_TEXT,
                   label + ": " + DoubleToString(price, _Digits));
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, name, OBJPROP_BACK,       true);
   ObjectSetInteger(0, name, OBJPROP_HIDDEN,     true);
  }

void _DeleteAll()
  {
   int total = ObjectsTotal(0);
   for(int i = total - 1; i >= 0; i--)
     {
      string n = ObjectName(0, i);
      if(StringFind(n, "smc_") == 0)
         ObjectDelete(0, n);
     }
  }

string _Line(int n)
  {
   string s = "";
   for(int i = 0; i < n; i++) s += "─";
   return s;
  }
//+------------------------------------------------------------------+
