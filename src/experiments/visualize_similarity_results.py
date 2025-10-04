"""
Visualization of Embedding Similarity Comparison Results

This script creates visualizations for the embedding similarity analysis,
showing distributions and comparisons between matched and unmatched pairs.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List


class SimilarityVisualizer:
    """Visualizer for similarity comparison results"""
    
    def __init__(self, results_file: str = "outputs/embeddings/similarity_comparison_results.json"):
        self.results_file = Path(results_file)
        self.results = None
        self.matched = None
        self.unmatched = None
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def load_results(self):
        """Load results from JSON file"""
        print(f"Loading results from {self.results_file}...")
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        
        self.matched = np.array(self.results['raw_similarities']['matched'])
        self.unmatched = np.array(self.results['raw_similarities']['unmatched'])
        
        print(f"✓ Loaded {len(self.matched)} matched and {len(self.unmatched)} unmatched similarities")
    
    def create_histogram_comparison(self, output_file: str = "outputs/embeddings/similarity_histogram.png"):
        """Create overlapping histograms for matched and unmatched similarities"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot histograms
        ax.hist(self.matched, bins=50, alpha=0.6, label='Matched Pairs', color='green', density=True)
        ax.hist(self.unmatched, bins=50, alpha=0.6, label='Unmatched Pairs', color='red', density=True)
        
        # Add mean lines
        ax.axvline(np.mean(self.matched), color='darkgreen', linestyle='--', linewidth=2, 
                   label=f'Matched Mean: {np.mean(self.matched):.4f}')
        ax.axvline(np.mean(self.unmatched), color='darkred', linestyle='--', linewidth=2, 
                   label=f'Unmatched Mean: {np.mean(self.unmatched):.4f}')
        
        ax.set_xlabel('Cosine Similarity', fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.set_title('Distribution of Cosine Similarities: Matched vs Unmatched Pairs', 
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved histogram to {output_file}")
        plt.close()
    
    def create_box_plot_comparison(self, output_file: str = "outputs/embeddings/similarity_boxplot.png"):
        """Create box plots comparing matched and unmatched similarities"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        data = [self.matched, self.unmatched]
        labels = ['Matched Pairs\n(Student_A ↔ Project_A)', 'Unmatched Pairs\n(Student_not_A ↔ Project_A)']
        
        bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.6)
        
        # Color the boxes
        colors = ['lightgreen', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # Add mean markers
        means = [np.mean(d) for d in data]
        ax.plot([1, 2], means, 'D', color='blue', markersize=10, label='Mean', zorder=3)
        
        # Add statistics text
        stats_text = f"Matched: μ={np.mean(self.matched):.4f}, σ={np.std(self.matched):.4f}\n"
        stats_text += f"Unmatched: μ={np.mean(self.unmatched):.4f}, σ={np.std(self.unmatched):.4f}\n"
        stats_text += f"Difference: Δμ={np.mean(self.matched) - np.mean(self.unmatched):.4f}\n"
        stats_text += f"Cohen's d: {self.results['analysis']['comparison']['effect_size_cohens_d']:.4f}"
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_ylabel('Cosine Similarity', fontsize=12)
        ax.set_title('Comparison of Cosine Similarities: Matched vs Unmatched Pairs', 
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved box plot to {output_file}")
        plt.close()
    
    def create_violin_plot(self, output_file: str = "outputs/embeddings/similarity_violin.png"):
        """Create violin plots showing distribution shapes"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        data = [self.matched, self.unmatched]
        labels = ['Matched', 'Unmatched']
        
        parts = ax.violinplot(data, positions=[1, 2], showmeans=True, showmedians=True, widths=0.7)
        
        # Color the violins
        colors = ['green', 'red']
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.6)
        
        ax.set_xticks([1, 2])
        ax.set_xticklabels(labels)
        ax.set_ylabel('Cosine Similarity', fontsize=12)
        ax.set_title('Distribution Shape Comparison: Matched vs Unmatched Pairs', 
                     fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved violin plot to {output_file}")
        plt.close()
    
    def create_cumulative_distribution(self, output_file: str = "outputs/embeddings/similarity_cdf.png"):
        """Create cumulative distribution function plot"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Sort data for CDF
        matched_sorted = np.sort(self.matched)
        unmatched_sorted = np.sort(self.unmatched)
        
        # Calculate CDF
        matched_cdf = np.arange(1, len(matched_sorted) + 1) / len(matched_sorted)
        unmatched_cdf = np.arange(1, len(unmatched_sorted) + 1) / len(unmatched_sorted)
        
        # Plot CDFs
        ax.plot(matched_sorted, matched_cdf, linewidth=2, color='green', 
                label='Matched Pairs', alpha=0.8)
        ax.plot(unmatched_sorted, unmatched_cdf, linewidth=2, color='red', 
                label='Unmatched Pairs', alpha=0.8)
        
        # Add reference lines
        ax.axhline(0.5, color='gray', linestyle=':', alpha=0.5)
        ax.axvline(np.median(self.matched), color='darkgreen', linestyle='--', alpha=0.5)
        ax.axvline(np.median(self.unmatched), color='darkred', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Cosine Similarity', fontsize=12)
        ax.set_ylabel('Cumulative Probability', fontsize=12)
        ax.set_title('Cumulative Distribution: Matched vs Unmatched Pairs', 
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved CDF plot to {output_file}")
        plt.close()
    
    def create_summary_dashboard(self, output_file: str = "outputs/embeddings/similarity_dashboard.png"):
        """Create a comprehensive dashboard with multiple plots"""
        fig = plt.figure(figsize=(16, 12))
        
        # Create grid
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Histogram (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(self.matched, bins=40, alpha=0.6, label='Matched', color='green', density=True)
        ax1.hist(self.unmatched, bins=40, alpha=0.6, label='Unmatched', color='red', density=True)
        ax1.axvline(np.mean(self.matched), color='darkgreen', linestyle='--', linewidth=2)
        ax1.axvline(np.mean(self.unmatched), color='darkred', linestyle='--', linewidth=2)
        ax1.set_xlabel('Cosine Similarity')
        ax1.set_ylabel('Density')
        ax1.set_title('Distribution Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Box plot (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        data = [self.matched, self.unmatched]
        bp = ax2.boxplot(data, labels=['Matched', 'Unmatched'], patch_artist=True)
        for patch, color in zip(bp['boxes'], ['lightgreen', 'lightcoral']):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax2.set_ylabel('Cosine Similarity')
        ax2.set_title('Box Plot Comparison')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. CDF (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        matched_sorted = np.sort(self.matched)
        unmatched_sorted = np.sort(self.unmatched)
        matched_cdf = np.arange(1, len(matched_sorted) + 1) / len(matched_sorted)
        unmatched_cdf = np.arange(1, len(unmatched_sorted) + 1) / len(unmatched_sorted)
        ax3.plot(matched_sorted, matched_cdf, linewidth=2, color='green', label='Matched')
        ax3.plot(unmatched_sorted, unmatched_cdf, linewidth=2, color='red', label='Unmatched')
        ax3.set_xlabel('Cosine Similarity')
        ax3.set_ylabel('Cumulative Probability')
        ax3.set_title('Cumulative Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Violin plot (middle right)
        ax4 = fig.add_subplot(gs[1, 1])
        parts = ax4.violinplot(data, positions=[1, 2], showmeans=True, showmedians=True)
        for pc, color in zip(parts['bodies'], ['green', 'red']):
            pc.set_facecolor(color)
            pc.set_alpha(0.6)
        ax4.set_xticks([1, 2])
        ax4.set_xticklabels(['Matched', 'Unmatched'])
        ax4.set_ylabel('Cosine Similarity')
        ax4.set_title('Violin Plot')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. Statistics table (bottom)
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('tight')
        ax5.axis('off')
        
        # Create statistics table
        stats_data = [
            ['Metric', 'Matched Pairs', 'Unmatched Pairs', 'Difference'],
            ['Count', f"{len(self.matched)}", f"{len(self.unmatched)}", ''],
            ['Mean', f"{np.mean(self.matched):.4f}", f"{np.mean(self.unmatched):.4f}", 
             f"{np.mean(self.matched) - np.mean(self.unmatched):.4f}"],
            ['Std Dev', f"{np.std(self.matched):.4f}", f"{np.std(self.unmatched):.4f}", ''],
            ['Median', f"{np.median(self.matched):.4f}", f"{np.median(self.unmatched):.4f}", 
             f"{np.median(self.matched) - np.median(self.unmatched):.4f}"],
            ['Min', f"{np.min(self.matched):.4f}", f"{np.min(self.unmatched):.4f}", ''],
            ['Max', f"{np.max(self.matched):.4f}", f"{np.max(self.unmatched):.4f}", ''],
            ['Q25', f"{np.percentile(self.matched, 25):.4f}", 
             f"{np.percentile(self.unmatched, 25):.4f}", ''],
            ['Q75', f"{np.percentile(self.matched, 75):.4f}", 
             f"{np.percentile(self.unmatched, 75):.4f}", ''],
            ['', '', '', ''],
            ['Effect Size (Cohen\'s d)', '', '', 
             f"{self.results['analysis']['comparison']['effect_size_cohens_d']:.4f}"]
        ]
        
        table = ax5.table(cellText=stats_data, cellLoc='center', loc='center',
                         colWidths=[0.25, 0.25, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Color header row
        for i in range(4):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color effect size row
        for i in range(4):
            table[(10, i)].set_facecolor('#FFF9C4')
            table[(10, i)].set_text_props(weight='bold')
        
        # Main title
        fig.suptitle('Embedding Similarity Analysis Dashboard', fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved dashboard to {output_file}")
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("\n=== Generating Visualizations ===")
        
        self.load_results()
        
        self.create_histogram_comparison()
        self.create_box_plot_comparison()
        self.create_violin_plot()
        self.create_cumulative_distribution()
        self.create_summary_dashboard()
        
        print("\n✓ All visualizations generated successfully")


def main():
    """Main execution function"""
    print("=" * 80)
    print("SIMILARITY RESULTS VISUALIZATION")
    print("=" * 80)
    
    visualizer = SimilarityVisualizer()
    visualizer.generate_all_visualizations()
    
    print("\n" + "=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  • outputs/embeddings/similarity_histogram.png")
    print("  • outputs/embeddings/similarity_boxplot.png")
    print("  • outputs/embeddings/similarity_violin.png")
    print("  • outputs/embeddings/similarity_cdf.png")
    print("  • outputs/embeddings/similarity_dashboard.png")


if __name__ == "__main__":
    main()


