import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_er_diagram():
    G = nx.DiGraph()
    
    # Define nodes with labels
    nodes = [
        'Client', 'Account', 'Transaction', 
        'Device', 'IPAddress', 'ClientRelationship',
        'Rule', 'Blacklist'
    ]
    G.add_nodes_from(nodes)
    
    # Define edges (relationships)
    edges = [
        ('Client', 'Account'),
        ('Client', 'ClientRelationship'),
        ('Account', 'Transaction'),
        ('Transaction', 'Device'),
        ('Transaction', 'IPAddress'),
        ('Rule', 'Transaction'), # Conceptual link
        ('Blacklist', 'Client')  # Conceptual link
    ]
    G.add_edges_from(edges)
    
    plt.figure(figsize=(10, 6))
    
    # Layout
    pos = nx.spring_layout(G, seed=42, k=1.5)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', alpha=0.9, node_shape='s')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, arrowsize=20)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    plt.title("ER Diagram: Anti-Fraud System", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('er_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated er_diagram.png")

def create_high_level_diagram():
    G = nx.DiGraph()
    
    # Define groups as nodes
    nodes = ['Users', 'Finance', 'Network', 'Security']
    G.add_nodes_from(nodes)
    
    # Define flows
    edges = [
        ('Users', 'Finance'),
        ('Finance', 'Network'),
        ('Network', 'Security'),
        ('Security', 'Finance') # Feedback loop (blocking)
    ]
    G.add_edges_from(edges)
    
    plt.figure(figsize=(8, 6))
    
    pos = nx.circular_layout(G)
    
    # Color map
    colors = ['#e1f5fe', '#e8f5e9', '#fff3e0', '#fce4ec']
    
    nx.draw_networkx_nodes(G, pos, node_size=5000, node_color=colors, alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=3, alpha=0.6, arrowsize=30, connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    
    plt.title("High-Level Architecture", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('high_level_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated high_level_diagram.png")

if __name__ == "__main__":
    try:
        create_er_diagram()
        create_high_level_diagram()
    except Exception as e:
        print(f"Error generating diagrams: {e}")
