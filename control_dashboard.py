import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import json
import os
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

ALL_LOCATIONS = [
    'Chennai', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Kolkata', 
    'Ahmedabad', 'Pune', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 'Nagpur', 
    'Indore', 'Bhopal', 'Visakhapatnam', 'Patna', 'Vadodara', 'Coimbatore', 
    'Ludhiana', 'Kochi', 'Guwahati', 'Chandigarh', 'Agra', 'Varanasi', 
    'Amritsar', 'Allahabad', 'Ranchi', 'Bhubaneswar', 'Dehradun', 'Raipur', 
    'Thiruvananthapuram', 'Mysuru', 'Madurai', 'Tirupati', 'Vijayawada', 
    'Mangalore', 'Nashik', 'Aurangabad', 'Rajkot', 'Jodhpur', 'Udaipur', 
    'Jammu', 'Shimla', 'Gurgaon', 'Noida', 'Faridabad', 'Ghaziabad', 'Meerut',
    'Vellore', 'Salem', 'Trichy', 'Tirunelveli', 'Guntur', 'Warangal', 
    'Karimnagar', 'Rajahmundry', 'Nellore', 'Kadapa', 'Kakinada', 'Hubli', 
    'Belgaum', 'Gulbarga', 'Jamshedpur', 'Dhanbad', 'Siliguri', 'Asansol', 
    'Durgapur', 'Panchkula', 'Mohali', 'Zirakpur', 'Dharamshala', 'Manali',
    'Rishikesh', 'Haridwar', 'Muzaffarpur', 'Purnia', 'Darbhanga', 'Bhagalpur',
    'Kurnool', 'Anantapur', 'Chittoor', 'Ongole', 'Nizamabad', 'Khammam',
    'Mahbubnagar', 'Tumkur', 'Davangere', 'Bellary', 'Bijapur', 'Shimoga',
    'Erode', 'Thanjavur', 'Dindigul', 'Vellankanni', 'Cuddalore', 'Kumbakonam',
    'Palakkad', 'Thrissur', 'Kannur', 'Kollam', 'Alappuzha', 'Kottayam',
    'Kozhikode', 'Tiruppur', 'Karur', 'Namakkal', 'Puducherry', 'Bikaner',
    'Ajmer', 'Kota', 'Bharatpur', 'Alwar', 'Bhilwara', 'Sikar', 'Pali',
    'Gorakhpur', 'Bareilly', 'Moradabad', 'Aligarh', 'Saharanpur', 'Mathura',
    'Firozabad', 'Jhansi', 'Gwalior', 'Ujjain', 'Jabalpur', 'Guna', 'Sagar',
    'Satna', 'Ratlam', 'Bilaspur', 'Korba', 'Raigarh', 'Bhilai', 'Kolhapur',
    'Sangli', 'Solapur', 'Nanded', 'Jalgaon', 'Amravati', 'Akola', 'Latur',
    'Dhule', 'Ahmednagar', 'Bhavnagar', 'Jamnagar', 'Junagadh', 'Gandhinagar',
    'Anand', 'Nadiad', 'Morbi', 'Surendranagar', 'Gandhidham'
]

def load_config():
    try:
        if os.path.exists('simulation_config.json'):
            with open('simulation_config.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return {
        'num_viewers': 100,
        'cache_size_mb': 100,
        'cache_ttl': 30,
        'origin_latency': 850,
        'origin_city': 'Chennai',
        'cities_enabled': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'],
        'running': False,
        'started_at': None
    }

def save_config(config):
    try:
        with open('simulation_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_uptime(started_at):
    if not started_at:
        return "Not running"
    try:
        start = datetime.fromisoformat(started_at)
        delta = datetime.now() - start
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except:
        return "Unknown"

# Layout
app.layout = html.Div([
    dcc.Interval(id='status-interval', interval=1000, n_intervals=0),
    
    # Header
    html.Div([
        html.Div([
            html.H1("EdgeStream Control Panel", style={
                'margin': '0', 'fontSize': '32px', 'fontWeight': '700',
                'background': 'linear-gradient(135deg, #667eea, #764ba2)',
                'WebkitBackgroundClip': 'text', 'WebkitTextFillColor': 'transparent',
            }),
            html.Div('Configure and monitor CDN simulation in real-time', 
                    style={'fontSize': '14px', 'color': '#64748b', 'marginTop': '8px'})
        ]),
        html.Div(id='header-status', style={'position': 'absolute', 'right': '40px', 'top': '30px'})
    ], style={
        'position': 'sticky', 'top': '0', 'zIndex': '1000',
        'padding': '30px 40px', 'backgroundColor': '#ffffff',
        'borderBottom': '1px solid #e5e7eb',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'backdropFilter': 'blur(10px)'
    }),
    
    html.Div([
        # Status Dashboard
        html.Div([
            html.H3('📊 Live Status', style={
                'fontSize': '20px', 'fontWeight': '600', 'color': '#1f2937', 'marginBottom': '20px'
            }),
            html.Div([
                html.Div([
                    html.Div('Status', style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px', 'fontWeight': '500'}),
                    html.Div(id='status-state', children='OFFLINE', style={
                        'fontSize': '24px', 'fontWeight': '700', 'color': '#ef4444'
                    })
                ], style={
                    'flex': '1', 'padding': '24px', 'backgroundColor': '#ffffff',
                    'borderRadius': '12px', 'textAlign': 'center', 'marginRight': '15px',
                    'border': '2px solid #e5e7eb', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                }),
                html.Div([
                    html.Div('Uptime', style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px', 'fontWeight': '500'}),
                    html.Div(id='status-uptime', children='00:00:00', style={
                        'fontSize': '24px', 'fontWeight': '700', 'color': '#3b82f6'
                    })
                ], style={
                    'flex': '1', 'padding': '24px', 'backgroundColor': '#ffffff',
                    'borderRadius': '12px', 'textAlign': 'center', 'marginRight': '15px',
                    'border': '2px solid #e5e7eb', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                }),
                html.Div([
                    html.Div('Origin', style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px', 'fontWeight': '500'}),
                    html.Div(id='status-origin', children='Chennai', style={
                        'fontSize': '24px', 'fontWeight': '700', 'color': '#f59e0b'
                    })
                ], style={
                    'flex': '1', 'padding': '24px', 'backgroundColor': '#ffffff',
                    'borderRadius': '12px', 'textAlign': 'center', 'marginRight': '15px',
                    'border': '2px solid #e5e7eb', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                }),
                html.Div([
                    html.Div('Caches', style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px', 'fontWeight': '500'}),
                    html.Div(id='status-caches', children='6', style={
                        'fontSize': '24px', 'fontWeight': '700', 'color': '#10b981'
                    })
                ], style={
                    'flex': '1', 'padding': '24px', 'backgroundColor': '#ffffff',
                    'borderRadius': '12px', 'textAlign': 'center',
                    'border': '2px solid #e5e7eb', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                }),
            ], style={'display': 'flex'}),
        ], style={
            'padding': '30px', 'backgroundColor': '#f9fafb', 
            'borderRadius': '16px', 'marginBottom': '25px',
            'border': '1px solid #e5e7eb'
        }),
        
        # Origin Server
        html.Div([
            html.H3('🎯 Origin Server', style={
                'fontSize': '20px', 'fontWeight': '600', 'color': '#1f2937', 'marginBottom': '10px'
            }),
            html.Div('Select the primary origin server location', 
                    style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '18px'}),
            dcc.Dropdown(
                id='origin-dropdown',
                options=[{'label': city, 'value': city} for city in ALL_LOCATIONS],
                value='Chennai',
                clearable=False,
                style={
                    'backgroundColor': '#ffffff',
                    'border': '2px solid #e5e7eb',
                    'borderRadius': '10px'
                }
            ),
            html.Div(id='origin-validation', style={'fontSize': '12px', 'color': '#10b981', 'marginTop': '8px', 'fontWeight': '500'})
        ], style={
            'padding': '30px', 'backgroundColor': '#ffffff', 
            'borderRadius': '16px', 'marginBottom': '25px',
            'border': '2px solid #fecaca', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
        }),
        
        # Cache Locations with Select All
        html.Div([
            html.Div([
                html.H3('📍 Cache Server Locations', style={
                    'fontSize': '20px', 'fontWeight': '600', 'color': '#1f2937', 'marginBottom': '10px', 'flex': '1'
                }),
                html.Div([
                    html.Button([
                        html.Span('✓ ', style={'marginRight': '5px'}),
                        'Select All'
                    ], id='select-all-btn', n_clicks=0, style={
                        'padding': '8px 16px', 'fontSize': '13px', 'fontWeight': '600',
                        'backgroundColor': '#3b82f6', 'color': 'white',
                        'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer',
                        'marginRight': '10px', 'transition': 'all 0.2s'
                    }),
                    html.Button([
                        html.Span('✕ ', style={'marginRight': '5px'}),
                        'Clear All'
                    ], id='clear-all-btn', n_clicks=0, style={
                        'padding': '8px 16px', 'fontSize': '13px', 'fontWeight': '600',
                        'backgroundColor': '#ef4444', 'color': 'white',
                        'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer',
                        'transition': 'all 0.2s'
                    })
                ])
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            
            html.Div('Enable CDN edge cache servers (minimum 4 locations)', 
                    style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '18px'}),
            dcc.Dropdown(
                id='cities-dropdown',
                options=[{'label': city, 'value': city} for city in ALL_LOCATIONS],
                value=['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'],
                multi=True,
                placeholder="Select cache locations...",
                style={
                    'backgroundColor': '#ffffff',
                    'border': '2px solid #e5e7eb',
                    'borderRadius': '10px'
                }
            ),
            html.Div(id='cities-validation', style={'fontSize': '12px', 'marginTop': '8px', 'fontWeight': '500'})
        ], style={
            'padding': '30px', 'backgroundColor': '#ffffff', 
            'borderRadius': '16px', 'marginBottom': '25px',
            'border': '2px solid #bfdbfe', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
        }),
        
        # Simulation Parameters
        html.Div([
            html.H3('⚙️ Simulation Parameters', style={
                'fontSize': '20px', 'fontWeight': '600', 'color': '#1f2937', 'marginBottom': '25px'
            }),
            
            # Grid Layout for Parameters
            html.Div([
                # Column 1
                html.Div([
                    html.Label('Number of Viewers', 
                              style={'fontSize': '14px', 'color': '#374151', 'marginBottom': '10px', 
                                    'display': 'block', 'fontWeight': '600'}),
                    html.Div([
                        dcc.Input(
                            id='num-viewers',
                            type='number',
                            value=100,
                            min=10,
                            max=100000,
                            step=10,
                            style={
                                'width': '100%', 'padding': '12px 16px', 
                                'backgroundColor': '#ffffff', 
                                'border': '2px solid #e5e7eb',
                                'borderRadius': '10px', 'color': '#1f2937',
                                'fontSize': '16px', 'fontWeight': '600'
                            }
                        ),
                        html.Div('viewers', style={
                            'position': 'absolute', 'right': '16px', 'top': '50%',
                            'transform': 'translateY(-50%)', 'color': '#9ca3af',
                            'fontSize': '14px', 'pointerEvents': 'none', 'fontWeight': '500'
                        })
                    ], style={'position': 'relative'}),
                    html.Div('Concurrent viewers', 
                            style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '8px'})
                ], style={'flex': '1', 'marginRight': '20px'}),
                
                # Column 2
                html.Div([
                    html.Label('Cache Size', 
                              style={'fontSize': '14px', 'color': '#374151', 'marginBottom': '10px', 
                                    'display': 'block', 'fontWeight': '600'}),
                    html.Div([
                        dcc.Input(
                            id='cache-size',
                            type='number',
                            value=100,
                            min=10,
                            max=10000,
                            step=10,
                            style={
                                'width': '100%', 'padding': '12px 16px', 
                                'backgroundColor': '#ffffff',
                                'border': '2px solid #e5e7eb',
                                'borderRadius': '10px', 'color': '#1f2937',
                                'fontSize': '16px', 'fontWeight': '600'
                            }
                        ),
                        html.Div('MB', style={
                            'position': 'absolute', 'right': '16px', 'top': '50%',
                            'transform': 'translateY(-50%)', 'color': '#9ca3af',
                            'fontSize': '14px', 'pointerEvents': 'none', 'fontWeight': '500'
                        })
                    ], style={'position': 'relative'}),
                    html.Div('Per server', 
                            style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '8px'})
                ], style={'flex': '1', 'marginRight': '20px'}),
                
                # Column 3
                html.Div([
                    html.Label('Origin Latency', 
                              style={'fontSize': '14px', 'color': '#374151', 'marginBottom': '10px', 
                                    'display': 'block', 'fontWeight': '600'}),
                    html.Div([
                        dcc.Input(
                            id='origin-latency',
                            type='number',
                            value=850,
                            min=100,
                            max=5000,
                            step=50,
                            style={
                                'width': '100%', 'padding': '12px 16px', 
                                'backgroundColor': '#ffffff',
                                'border': '2px solid #e5e7eb',
                                'borderRadius': '10px', 'color': '#1f2937',
                                'fontSize': '16px', 'fontWeight': '600'
                            }
                        ),
                        html.Div('ms', style={
                            'position': 'absolute', 'right': '16px', 'top': '50%',
                            'transform': 'translateY(-50%)', 'color': '#9ca3af',
                            'fontSize': '14px', 'pointerEvents': 'none', 'fontWeight': '500'
                        })
                    ], style={'position': 'relative'}),
                    html.Div('Distance penalty', 
                            style={'fontSize': '12px', 'color': '#6b7280', 'marginTop': '8px'})
                ], style={'flex': '1'}),
                
            ], style={'display': 'flex'}),
            
        ], style={
            'padding': '30px', 'backgroundColor': '#ffffff', 
            'borderRadius': '16px', 'marginBottom': '30px',
            'border': '2px solid #fde68a', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
        }),
        
        # Control Buttons
        html.Div([
            html.Button([
                html.Span('▶️', style={'marginRight': '10px', 'fontSize': '20px'}),
                'START SIMULATION'
            ], id='start-btn', n_clicks=0, style={
                'padding': '18px 40px', 'fontSize': '16px', 'fontWeight': '700',
                'backgroundColor': '#10b981', 'color': 'white',
                'border': 'none', 'borderRadius': '12px', 'cursor': 'pointer',
                'marginRight': '20px', 'boxShadow': '0 4px 15px rgba(16, 185, 129, 0.3)',
                'transition': 'all 0.3s ease'
            }),
            html.Button([
                html.Span('⏹️', style={'marginRight': '10px', 'fontSize': '20px'}),
                'STOP SIMULATION'
            ], id='stop-btn', n_clicks=0, style={
                'padding': '18px 40px', 'fontSize': '16px', 'fontWeight': '700',
                'backgroundColor': '#ef4444', 'color': 'white',
                'border': 'none', 'borderRadius': '12px', 'cursor': 'pointer',
                'marginRight': '20px', 'boxShadow': '0 4px 15px rgba(239, 68, 68, 0.3)',
                'transition': 'all 0.3s ease'
            }),
            html.Button([
                html.Span('🔄', style={'marginRight': '10px', 'fontSize': '20px'}),
                'RESET'
            ], id='reset-btn', n_clicks=0, style={
                'padding': '18px 40px', 'fontSize': '16px', 'fontWeight': '700',
                'backgroundColor': '#ffffff', 'color': '#6b7280',
                'border': '2px solid #e5e7eb',
                'borderRadius': '12px', 'cursor': 'pointer',
                'transition': 'all 0.3s ease'
            }),
        ], style={'textAlign': 'center', 'marginBottom': '25px'}),
        
        # Status Message
        html.Div(id='control-message', style={
            'textAlign': 'center', 'padding': '20px',
            'backgroundColor': '#f9fafb',
            'borderRadius': '12px', 'fontSize': '15px',
            'border': '2px solid #e5e7eb'
        }),
        
    ], style={'maxWidth': '1000px', 'margin': '40px auto', 'padding': '0 20px', 'paddingBottom': '60px'}),
    
], style={
    'backgroundColor': '#f3f4f6', 
    'minHeight': '100vh', 
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
})

# Callbacks
@app.callback(
    [Output('status-state', 'children'),
     Output('status-state', 'style'),
     Output('status-uptime', 'children'),
     Output('status-origin', 'children'),
     Output('status-caches', 'children'),
     Output('header-status', 'children')],
    Input('status-interval', 'n_intervals')
)
def update_status(n):
    config = load_config()
    running = config.get('running', False)
    
    if running:
        status_text = 'LIVE'
        status_style = {'fontSize': '24px', 'fontWeight': '700', 'color': '#10b981'}
        uptime = get_uptime(config.get('started_at'))
        badge = html.Div('● LIVE', style={
            'padding': '10px 20px', 'backgroundColor': '#10b981',
            'color': 'white', 'borderRadius': '20px',
            'fontSize': '14px', 'fontWeight': '700'
        })
    else:
        status_text = 'OFFLINE'
        status_style = {'fontSize': '24px', 'fontWeight': '700', 'color': '#ef4444'}
        uptime = '00:00:00'
        badge = html.Div('● OFFLINE', style={
            'padding': '10px 20px', 'backgroundColor': '#e5e7eb',
            'color': '#6b7280', 'borderRadius': '20px',
            'fontSize': '14px', 'fontWeight': '700'
        })
    
    origin = config.get('origin_city', 'Chennai')
    num_caches = len(config.get('cities_enabled', []))
    
    return status_text, status_style, uptime, origin, str(num_caches), badge

@app.callback(
    Output('cities-dropdown', 'value'),
    [Input('select-all-btn', 'n_clicks'),
     Input('clear-all-btn', 'n_clicks')],
    [State('cities-dropdown', 'value')]
)
def select_clear_all(select_clicks, clear_clicks, current_value):
    ctx = callback_context
    if not ctx.triggered:
        return current_value
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == 'select-all-btn':
        return ALL_LOCATIONS  # Select all
    elif trigger == 'clear-all-btn':
        return []  # Clear all
    
    return current_value

@app.callback(
    Output('origin-validation', 'children'),
    Input('origin-dropdown', 'value')
)
def validate_origin(origin):
    if origin:
        return f"✓ Origin set to {origin}"
    return "⚠️ Please select an origin server"

@app.callback(
    [Output('cities-validation', 'children'),
     Output('cities-validation', 'style')],
    Input('cities-dropdown', 'value')
)
def validate_cities(cities):
    if not cities or len(cities) < 4:
        return f"⚠️ Select at least 4 cache locations (currently {len(cities) if cities else 0})", {'color': '#f59e0b'}
    return f"✓ {len(cities)} cache locations selected", {'color': '#10b981'}

@app.callback(
    Output('control-message', 'children'),
    [Input('start-btn', 'n_clicks'),
     Input('stop-btn', 'n_clicks'),
     Input('reset-btn', 'n_clicks')],
    [State('origin-dropdown', 'value'),
     State('cities-dropdown', 'value'),
     State('num-viewers', 'value'),
     State('cache-size', 'value'),
     State('origin-latency', 'value')]
)
def control_actions(start_clicks, stop_clicks, reset_clicks, origin, cities, num_viewers, cache_size, origin_latency):
    ctx = callback_context
    if not ctx.triggered:
        config = load_config()
        if config.get('running'):
            return html.Div([
                html.Span('✅ ', style={'fontSize': '20px', 'marginRight': '10px'}),
                f"Simulation RUNNING • Origin: {config.get('origin_city')} • {config.get('num_viewers'):,} viewers • {len(config.get('cities_enabled', []))} caches"
            ], style={'color': '#10b981', 'fontWeight': '600'})
        return html.Div([
            html.Span('⏸️ ', style={'fontSize': '20px', 'marginRight': '10px'}),
            "Ready to start. Configure parameters and click START."
        ], style={'color': '#6b7280'})
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == 'start-btn':
        if not cities or len(cities) < 4:
            return html.Div([
                html.Span('❌ ', style={'fontSize': '20px', 'marginRight': '10px'}),
                f"Cannot start: Need at least 4 cache locations (selected: {len(cities) if cities else 0})"
            ], style={'color': '#ef4444', 'fontWeight': '600'})
        
        config = {
            'num_viewers': num_viewers,
            'cache_size_mb': cache_size,
            'cache_ttl': 30,
            'origin_latency': origin_latency,
            'origin_city': origin,
            'cities_enabled': cities,
            'running': True,
            'started_at': datetime.now().isoformat()
        }
        if save_config(config):
            return html.Div([
                html.Span('✅ ', style={'fontSize': '20px', 'marginRight': '10px'}),
                f"Simulation STARTED • Origin: {origin} • {num_viewers:,} viewers • {len(cities)} caches enabled"
            ], style={'color': '#10b981', 'fontWeight': '600'})
    
    elif trigger == 'stop-btn':
        config = load_config()
        config['running'] = False
        if save_config(config):
            return html.Div([
                html.Span('⏹️ ', style={'fontSize': '20px', 'marginRight': '10px'}),
                "Simulation STOPPED successfully"
            ], style={'color': '#ef4444', 'fontWeight': '600'})
    
    elif trigger == 'reset-btn':
        config = {
            'num_viewers': 100,
            'cache_size_mb': 100,
            'cache_ttl': 30,
            'origin_latency': 850,
            'origin_city': 'Chennai',
            'cities_enabled': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'],
            'running': False,
            'started_at': None
        }
        if save_config(config):
            return html.Div([
                html.Span('🔄 ', style={'fontSize': '20px', 'marginRight': '10px'}),
                "Configuration RESET to defaults"
            ], style={'color': '#3b82f6', 'fontWeight': '600'})
    
    return html.Div("Ready", style={'color': '#6b7280'})

if __name__ == '__main__':
    print("\n" + "="*80)
    print("⚙️ EdgeStream Control Dashboard - With Select All")
    print("="*80)
    print("🌐 http://localhost:8050/")
    print("\n✅ Features:")
    print("   • Select All / Clear All buttons")
    print("   • Improved grid layout")
    print("   • Clean white UI")
    print("   • Real-time validation")
    print("="*80 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=8050)
