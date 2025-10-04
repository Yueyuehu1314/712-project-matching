"""
Embedding-based Similarity Comparison for Project-Student Matching

This script generates embeddings for all projects and student profiles using bge-m3 model via Ollama,
then compares cosine similarity between matched and unmatched project-student pairs.

Research Question: Does vector cosine similarity effectively distinguish between 
matched (Student_A generated for Project_A) and unmatched pairs?
"""

import os
import json
import requests
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class DocumentEmbedding:
    """Container for document embedding with metadata"""
    file_path: str
    file_name: str
    doc_type: str  # "project" or "profile"
    content: str
    embedding: List[float]
    matched_project: str = None  # For profiles: which project they were generated for
    project_folder: str = None  # For profiles: parent folder name


class OllamaEmbeddingClient:
    """Client for generating embeddings using Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "bge-m3"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text using bge-m3 model"""
        try:
            url = f"{self.base_url}/api/embeddings"
            data = {
                "model": self.model,
                "prompt": text
            }
            
            response = self.session.post(url, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("embedding", [])
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []


class EmbeddingGenerator:
    """Generate embeddings for all projects and profiles"""
    
    def __init__(self, 
                 projects_dir: str = "data/processed/projects_md",
                 profiles_dir: str = "data/processed/profiles_md",
                 output_file: str = "outputs/embeddings/project_profile_embeddings.json"):
        self.projects_dir = Path(projects_dir)
        self.profiles_dir = Path(profiles_dir)
        self.output_file = Path(output_file)
        self.client = OllamaEmbeddingClient()
        
        # Create output directory if not exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def read_markdown_content(self, file_path: Path) -> str:
        """Read markdown file and extract content (excluding <think> tags)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove <think> sections if present
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
            
            return content.strip()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def extract_matched_project_from_profile(self, content: str) -> str:
        """Extract matched project name from profile content"""
        # Look for "## Matched Project" section
        match = re.search(r'##\s*Matched Project\s*\n\*\*Project Title\*\*:\s*(.+)', content)
        if match:
            return match.group(1).strip()
        return "Unknown"
    
    def extract_project_description_only(self, content: str) -> str:
        """
        Extract only the project description part from enhanced project files.
        Enhanced files contain: Project Description + Unit Outlines + Student Profiles
        We only want the Project Description for embedding.
        """
        # Find the first "---" separator that marks the end of project description
        lines = content.split('\n')
        project_desc_lines = []
        found_separator = False
        
        for line in lines:
            if line.strip() == '---' and not found_separator:
                # This is the end of project description
                found_separator = True
                break
            project_desc_lines.append(line)
        
        return '\n'.join(project_desc_lines).strip()
    
    def generate_project_embeddings(self) -> List[DocumentEmbedding]:
        """Generate embeddings for all project files"""
        embeddings = []
        project_files = list(self.projects_dir.glob("**/*.md"))
        
        print(f"\n=== Generating embeddings for {len(project_files)} projects ===")
        
        for idx, project_file in enumerate(project_files, 1):
            print(f"[{idx}/{len(project_files)}] Processing: {project_file.name}")
            
            content = self.read_markdown_content(project_file)
            if not content:
                continue
            
            # Extract only project description (not Unit Outlines or Student Profiles)
            project_desc = self.extract_project_description_only(content)
            print(f"  → Extracted project description: {len(project_desc)} chars (from {len(content)} total)")
            
            embedding = self.client.generate_embedding(project_desc)
            if not embedding:
                print(f"  Warning: Failed to generate embedding for {project_file.name}")
                continue
            
            doc_embedding = DocumentEmbedding(
                file_path=str(project_file),
                file_name=project_file.name,
                doc_type="project",
                content=project_desc[:500],  # Store first 500 chars for reference
                embedding=embedding
            )
            embeddings.append(doc_embedding)
        
        print(f"✓ Generated {len(embeddings)} project embeddings")
        return embeddings
    
    def generate_profile_embeddings(self) -> List[DocumentEmbedding]:
        """Generate embeddings for all student profile files"""
        embeddings = []
        
        # Profiles are organized by project folder
        project_folders = [d for d in self.profiles_dir.iterdir() if d.is_dir()]
        
        total_files = sum(len(list(folder.glob("*.md"))) for folder in project_folders)
        print(f"\n=== Generating embeddings for {total_files} profiles across {len(project_folders)} projects ===")
        
        processed = 0
        for project_folder in project_folders:
            profile_files = list(project_folder.glob("*.md"))
            
            for profile_file in profile_files:
                processed += 1
                print(f"[{processed}/{total_files}] Processing: {project_folder.name}/{profile_file.name}")
                
                content = self.read_markdown_content(profile_file)
                if not content:
                    continue
                
                embedding = self.client.generate_embedding(content)
                if not embedding:
                    print(f"  Warning: Failed to generate embedding for {profile_file.name}")
                    continue
                
                matched_project = self.extract_matched_project_from_profile(content)
                
                doc_embedding = DocumentEmbedding(
                    file_path=str(profile_file),
                    file_name=profile_file.name,
                    doc_type="profile",
                    content=content[:500],  # Store first 500 chars for reference
                    embedding=embedding,
                    matched_project=matched_project,
                    project_folder=project_folder.name
                )
                embeddings.append(doc_embedding)
        
        print(f"✓ Generated {len(embeddings)} profile embeddings")
        return embeddings
    
    def save_embeddings(self, embeddings: List[DocumentEmbedding]):
        """Save all embeddings to JSON file"""
        print(f"\n=== Saving embeddings to {self.output_file} ===")
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "model": self.client.model,
            "total_documents": len(embeddings),
            "embeddings": [asdict(emb) for emb in embeddings]
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(embeddings)} embeddings to {self.output_file}")
        
        # Print file size
        file_size_mb = self.output_file.stat().st_size / (1024 * 1024)
        print(f"  File size: {file_size_mb:.2f} MB")
    
    def generate_all_embeddings(self) -> str:
        """Generate embeddings for all projects and profiles"""
        # Check Ollama availability
        if not self.client.is_available():
            raise RuntimeError("Ollama service is not available. Please ensure Ollama is running.")
        
        print("✓ Ollama service is available")
        print(f"✓ Using model: {self.client.model}")
        
        # Generate embeddings
        project_embeddings = self.generate_project_embeddings()
        profile_embeddings = self.generate_profile_embeddings()
        
        all_embeddings = project_embeddings + profile_embeddings
        
        # Save to file
        self.save_embeddings(all_embeddings)
        
        return str(self.output_file)


class SimilarityComparator:
    """Compare cosine similarity between matched and unmatched pairs"""
    
    def __init__(self, embeddings_file: str):
        self.embeddings_file = Path(embeddings_file)
        self.embeddings_data = None
        self.projects = []
        self.profiles = []
    
    def load_embeddings(self):
        """Load embeddings from JSON file"""
        print(f"\n=== Loading embeddings from {self.embeddings_file} ===")
        
        with open(self.embeddings_file, 'r', encoding='utf-8') as f:
            self.embeddings_data = json.load(f)
        
        # Separate projects and profiles
        for emb_dict in self.embeddings_data['embeddings']:
            emb = DocumentEmbedding(**emb_dict)
            if emb.doc_type == "project":
                self.projects.append(emb)
            else:
                self.profiles.append(emb)
        
        print(f"✓ Loaded {len(self.projects)} projects and {len(self.profiles)} profiles")
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def is_matched_pair(self, project: DocumentEmbedding, profile: DocumentEmbedding) -> bool:
        """Check if a profile was generated for a specific project"""
        # Match based on project folder name
        project_name = Path(project.file_path).stem
        profile_folder = profile.project_folder
        
        # Handle different naming conventions
        return project_name in profile_folder or profile_folder in project_name
    
    def compute_all_similarities(self) -> Tuple[List[float], List[float]]:
        """
        Compute cosine similarities for all project-profile pairs
        
        Returns:
            matched_similarities: List of similarities for matched pairs
            unmatched_similarities: List of similarities for unmatched pairs
        """
        print("\n=== Computing cosine similarities ===")
        
        matched_similarities = []
        unmatched_similarities = []
        
        total_comparisons = len(self.projects) * len(self.profiles)
        print(f"Total comparisons: {total_comparisons:,}")
        
        comparison_count = 0
        for project in self.projects:
            project_name = Path(project.file_path).stem
            
            for profile in self.profiles:
                comparison_count += 1
                if comparison_count % 1000 == 0:
                    print(f"  Progress: {comparison_count:,}/{total_comparisons:,} comparisons")
                
                similarity = self.cosine_similarity(project.embedding, profile.embedding)
                
                if self.is_matched_pair(project, profile):
                    matched_similarities.append(similarity)
                else:
                    unmatched_similarities.append(similarity)
        
        print(f"✓ Computed {len(matched_similarities)} matched pairs")
        print(f"✓ Computed {len(unmatched_similarities)} unmatched pairs")
        
        return matched_similarities, unmatched_similarities
    
    def analyze_results(self, matched: List[float], unmatched: List[float]) -> Dict:
        """Analyze similarity distributions"""
        print("\n=== Analysis Results ===")
        
        matched_arr = np.array(matched)
        unmatched_arr = np.array(unmatched)
        
        results = {
            "matched_pairs": {
                "count": len(matched),
                "mean": float(np.mean(matched_arr)),
                "std": float(np.std(matched_arr)),
                "min": float(np.min(matched_arr)),
                "max": float(np.max(matched_arr)),
                "median": float(np.median(matched_arr)),
                "q25": float(np.percentile(matched_arr, 25)),
                "q75": float(np.percentile(matched_arr, 75))
            },
            "unmatched_pairs": {
                "count": len(unmatched),
                "mean": float(np.mean(unmatched_arr)),
                "std": float(np.std(unmatched_arr)),
                "min": float(np.min(unmatched_arr)),
                "max": float(np.max(unmatched_arr)),
                "median": float(np.median(unmatched_arr)),
                "q25": float(np.percentile(unmatched_arr, 25)),
                "q75": float(np.percentile(unmatched_arr, 75))
            },
            "comparison": {
                "mean_difference": float(np.mean(matched_arr) - np.mean(unmatched_arr)),
                "effect_size_cohens_d": float((np.mean(matched_arr) - np.mean(unmatched_arr)) / 
                                             np.sqrt((np.std(matched_arr)**2 + np.std(unmatched_arr)**2) / 2))
            }
        }
        
        # Print summary
        print("\n--- Matched Pairs (Student_A generated for Project_A) ---")
        print(f"  Count: {results['matched_pairs']['count']}")
        print(f"  Mean similarity: {results['matched_pairs']['mean']:.4f}")
        print(f"  Std deviation: {results['matched_pairs']['std']:.4f}")
        print(f"  Range: [{results['matched_pairs']['min']:.4f}, {results['matched_pairs']['max']:.4f}]")
        print(f"  Median: {results['matched_pairs']['median']:.4f}")
        
        print("\n--- Unmatched Pairs (Student_not_A vs Project_A) ---")
        print(f"  Count: {results['unmatched_pairs']['count']}")
        print(f"  Mean similarity: {results['unmatched_pairs']['mean']:.4f}")
        print(f"  Std deviation: {results['unmatched_pairs']['std']:.4f}")
        print(f"  Range: [{results['unmatched_pairs']['min']:.4f}, {results['unmatched_pairs']['max']:.4f}]")
        print(f"  Median: {results['unmatched_pairs']['median']:.4f}")
        
        print("\n--- Comparison ---")
        print(f"  Mean difference (matched - unmatched): {results['comparison']['mean_difference']:.4f}")
        print(f"  Cohen's d (effect size): {results['comparison']['effect_size_cohens_d']:.4f}")
        
        if results['comparison']['mean_difference'] > 0:
            print("  ✓ Matched pairs have HIGHER similarity (as expected)")
        else:
            print("  ✗ Warning: Unmatched pairs have higher similarity (unexpected)")
        
        return results
    
    def save_results(self, matched: List[float], unmatched: List[float], 
                    analysis: Dict, output_file: str = "outputs/embeddings/similarity_comparison_results.json"):
        """Save comparison results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            "generated_at": datetime.now().isoformat(),
            "embeddings_file": str(self.embeddings_file),
            "analysis": analysis,
            "raw_similarities": {
                "matched": matched,
                "unmatched": unmatched
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Results saved to {output_path}")
        
        # Print file size
        file_size_kb = output_path.stat().st_size / 1024
        print(f"  File size: {file_size_kb:.2f} KB")
    
    def run_comparison(self) -> Dict:
        """Run full similarity comparison pipeline"""
        self.load_embeddings()
        matched, unmatched = self.compute_all_similarities()
        analysis = self.analyze_results(matched, unmatched)
        self.save_results(matched, unmatched, analysis)
        
        return analysis


def main():
    """Main execution function"""
    print("=" * 80)
    print("EMBEDDING-BASED SIMILARITY COMPARISON")
    print("Research: Vector Cosine Similarity for Project-Student Matching")
    print("=" * 80)
    
    # Step 1: Generate embeddings
    print("\n[STEP 1] Generating embeddings for all projects and profiles...")
    generator = EmbeddingGenerator()
    embeddings_file = generator.generate_all_embeddings()
    
    # Step 2: Compare similarities
    print("\n[STEP 2] Comparing similarities between matched and unmatched pairs...")
    comparator = SimilarityComparator(embeddings_file)
    results = comparator.run_comparison()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey Findings:")
    print(f"  • Matched pairs show mean similarity: {results['matched_pairs']['mean']:.4f}")
    print(f"  • Unmatched pairs show mean similarity: {results['unmatched_pairs']['mean']:.4f}")
    print(f"  • Difference: {results['comparison']['mean_difference']:.4f}")
    print(f"  • Effect size (Cohen's d): {results['comparison']['effect_size_cohens_d']:.4f}")
    
    if results['comparison']['effect_size_cohens_d'] > 0.8:
        print("\n✓ STRONG effect: Vector similarity effectively distinguishes matched pairs")
    elif results['comparison']['effect_size_cohens_d'] > 0.5:
        print("\n✓ MODERATE effect: Vector similarity shows meaningful distinction")
    elif results['comparison']['effect_size_cohens_d'] > 0.2:
        print("\n~ WEAK effect: Vector similarity shows limited distinction")
    else:
        print("\n✗ NEGLIGIBLE effect: Vector similarity does not distinguish well")


if __name__ == "__main__":
    main()


