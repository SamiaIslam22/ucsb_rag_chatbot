import os
import sys
import time
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NanofabRAGPipeline:
    """Complete RAG Pipeline for Nanofab Knowledge Management"""
    
    def __init__(self):
        load_dotenv()
        self.base_dir = Path(__file__).parent.parent  # Go up to project root
        
    def check_existing_data(self):
        """Check what data files already exist"""
        logger.info("🔍 Checking existing data files...")
        
        files_to_check = {
            "Wiki Pages": "csv_dataframes/raw/wiki_all_page_links.csv",
            "Wiki Texts": "csv_dataframes/raw/wiki_texts.csv", 
            "Wiki Tables": "csv_dataframes/raw/wiki_tables.csv",
            "Wiki Images": "csv_dataframes/raw/wiki_images.csv"
        }
        
        existing_files = {}
        
        for name, filepath in files_to_check.items():
            # Check multiple possible locations
            possible_paths = [
                filepath,  # Relative to current dir
                self.base_dir / filepath,  # Relative to project root
                Path(filepath).absolute()  # Absolute from current dir
            ]
            
            found = False
            for path in possible_paths:
                if Path(path).exists():
                    existing_files[name] = path
                    import pandas as pd
                    try:
                        df = pd.read_csv(path)
                        logger.info(f"✅ {name}: Found with {len(df)} rows at {path}")
                        found = True
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ {name}: File exists but can't read: {e}")
            
            if not found:
                logger.warning(f"❌ {name}: Not found")
                
        return existing_files

    def debug_check_csv_files(self):
        """Debug: Check all CSV files exist before chunking"""
        logger.info("🔍 Debug: Checking all CSV files before chunking...")
        
        files_to_check = [
            "csv_dataframes/raw/wiki_texts.csv",
            "csv_dataframes/raw/wiki_tables.csv", 
            "csv_dataframes/raw/wiki_images.csv"
        ]
        
        missing_files = []
        for file_path in files_to_check:
            possible_paths = [
                file_path,
                self.base_dir / file_path,
                Path(file_path).absolute()
            ]
            
            found = False
            for path in possible_paths:
                if Path(path).exists():
                    try:
                        import pandas as pd
                        df = pd.read_csv(path)
                        logger.info(f"✅ {file_path}: Found with {len(df)} rows at {path}")
                        found = True
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ {file_path}: Exists but can't read: {e}")
            
            if not found:
                logger.error(f"❌ {file_path}: Missing!")
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing files will cause incomplete chunking: {missing_files}")
            logger.error("💡 Suggestion: Run the extraction steps first to generate these files")
            return False
        else:
            logger.info("✅ All CSV files found - chunking should include all content types")
            return True

    def step_1_extract_wiki_texts(self):
        """Step 1: Extract text content from wiki pages (or skip if exists)"""
        logger.info("📝 Step 1: Checking Wiki Text Extraction...")
        try:
            # Check if file already exists
            possible_paths = [
                "csv_dataframes/raw/wiki_texts.csv",
                self.base_dir / "csv_dataframes/raw/wiki_texts.csv",
                Path("csv_dataframes/raw/wiki_texts.csv").absolute()
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    import pandas as pd
                    df = pd.read_csv(path)
                    logger.info(f"✅ Step 1 Completed: Found existing wiki_texts.csv with {len(df)} rows at {path}")
                    return True
                    
            logger.info("📝 No existing wiki texts found, running extraction...")
            
            # Run extraction
            from extraction.wiki_texts import run_all_scrapes, load_wiki_urls_from_csv
            import pandas as pd
            
            urls = load_wiki_urls_from_csv()
            logger.info(f"📋 Processing {len(urls)} pages")
            
            scraped_data = asyncio.run(run_all_scrapes(urls))
            df = pd.DataFrame(scraped_data)
            
            # Save to the first location
            os.makedirs("csv_dataframes/raw", exist_ok=True)
            df.to_csv("csv_dataframes/raw/wiki_texts.csv", index=False)
            
            logger.info(f"✅ Step 1 Completed: Extracted text from {len(df)} pages")
            return True
            
        except Exception as e:
            logger.error(f"❌ Step 1 Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_2_extract_wiki_tables(self):
        """Step 2: Extract tables from wiki pages (or skip if exists)"""
        logger.info("📊 Step 2: Checking Wiki Table Extraction...")
        try:
            # Check if file already exists
            possible_paths = [
                "csv_dataframes/raw/wiki_tables.csv",
                self.base_dir / "csv_dataframes/raw/wiki_tables.csv", 
                Path("csv_dataframes/raw/wiki_tables.csv").absolute()
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    import pandas as pd
                    df = pd.read_csv(path)
                    tables_found = len(df[df['table_number'] != 'no_tables'])
                    logger.info(f"✅ Step 2 Completed: Found existing wiki_tables.csv with {tables_found} tables at {path}")
                    return True
                    
            logger.info("📊 No existing wiki tables found, running extraction...")
            
            # Run extraction  
            from extraction.wiki_table import main as extract_tables
            extract_tables()
            
            # Check if file was created
            for path in possible_paths:
                if Path(path).exists():
                    import pandas as pd
                    df = pd.read_csv(path)
                    tables_found = len(df[df['table_number'] != 'no_tables'])
                    logger.info(f"✅ Step 2 Completed: Extracted {tables_found} tables")
                    return True
                    
            logger.error("❌ Step 2 Failed: No output file created")
            return False
            
        except Exception as e:
            logger.error(f"❌ Step 2 Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_3_extract_wiki_images(self):
        """Step 3: Extract and process images from wiki pages (or skip if exists)"""
        logger.info("🖼️ Step 3: Checking Wiki Image Extraction...")
        try:
            # Check if file already exists
            possible_paths = [
                "csv_dataframes/raw/wiki_images.csv",
                self.base_dir / "csv_dataframes/raw/wiki_images.csv",
                Path("csv_dataframes/raw/wiki_images.csv").absolute()
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    import pandas as pd
                    df = pd.read_csv(path)
                    logger.info(f"✅ Step 3 Completed: Found existing wiki_images.csv with {len(df)} images at {path}")
                    return True
                    
            logger.info("🖼️ No existing wiki images found, running extraction...")
            
            # Run extraction
            from extraction.wiki_images import main as wiki_images_main
            asyncio.run(wiki_images_main())
            
            # Check if file was created
            for path in possible_paths:
                if Path(path).exists():
                    import pandas as pd
                    df = pd.read_csv(path)
                    logger.info(f"✅ Step 3 Completed: Processed {len(df)} images")
                    return True
                    
            logger.error("❌ Step 3 Failed: No output file created")
            return False
            
        except Exception as e:
            logger.error(f"❌ Step 3 Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_4_chunk_documents(self):
        """Step 4: Chunk all extracted documents"""
        logger.info("✂️ Step 4: Starting Document Chunking...")
        try:
            # Check multiple possible locations for the output file
            possible_paths = [
                "csv_dataframes/processed/chunked_pages.csv",  # Relative to current dir
                self.base_dir / "csv_dataframes/processed/chunked_pages.csv",  # Relative to project root
                Path("csv_dataframes/processed/chunked_pages.csv").absolute()  # Absolute from current dir
            ]
            
            # Check if file already exists
            existing_file = None
            for path in possible_paths:
                if Path(path).exists():
                    existing_file = path
                    break
                    
            if existing_file:
                import pandas as pd
                df = pd.read_csv(existing_file)
                logger.info(f"✅ Step 4 Completed: Found existing chunked_pages.csv with {len(df)} chunks at {existing_file}")
                return True
            
            # CRITICAL: Check that all required CSV files exist before chunking
            logger.info("🔍 Verifying all required CSV files exist before chunking...")
            if not self.debug_check_csv_files():
                logger.error("❌ Cannot proceed with chunking - missing required CSV files")
                logger.error("💡 Please ensure steps 1-3 completed successfully and generated all CSV files")
                return False
            
            # Create the output directory for all possible locations
            for path in possible_paths:
                os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Import and run chunking
            logger.info("🔄 Running chunking process...")
            import chunking.chunking
            
            # Wait a moment for chunking to complete
            time.sleep(3)  # Increased wait time
            
            # Check all possible locations for the output file after chunking
            found_file = None
            for path in possible_paths:
                if Path(path).exists():
                    found_file = path
                    break
                    
            if found_file:
                import pandas as pd
                df = pd.read_csv(found_file)
                
                # Check content type distribution
                content_types = df['content_type'].value_counts() if 'content_type' in df.columns else {}
                logger.info(f"✅ Step 4 Completed: Created {len(df)} chunks")
                logger.info(f"📁 File saved at: {found_file}")
                logger.info(f"📊 Content type distribution: {dict(content_types)}")
                
                # Warn if missing content types
                expected_types = ['text', 'table', 'table_row', 'image']
                missing_types = [t for t in expected_types if t not in content_types.index]
                if missing_types:
                    logger.warning(f"⚠️ Missing content types in chunks: {missing_types}")
                    logger.warning("💡 This suggests some extraction steps may have failed")
                
                return True
            else:
                logger.error("❌ Step 4 Failed: Chunking output file not created in any expected location")
                logger.error(f"❌ Searched locations:")
                for path in possible_paths:
                    logger.error(f"   - {path} (exists: {Path(path).exists()})")
                
                # List what files DO exist in the directories
                for path in possible_paths:
                    parent_dir = Path(path).parent
                    if parent_dir.exists():
                        files = list(parent_dir.glob("*.csv"))
                        logger.error(f"   Files in {parent_dir}: {[f.name for f in files]}")
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Step 4 Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_5_generate_embeddings(self):
        """Step 5: Generate embeddings for all chunks"""
        logger.info("🧠 Step 5: Starting Embedding Generation...")
        try:
            # Check multiple possible locations for the output file
            possible_output_paths = [
                "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                self.base_dir / "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                Path("csv_dataframes/embeddings/chunked_pages_with_embeddings.csv").absolute()
            ]
            
            # Check if embeddings file already exists
            existing_file = None
            for path in possible_output_paths:
                if Path(path).exists():
                    existing_file = path
                    break
                    
            if existing_file:
                import pandas as pd
                df = pd.read_csv(existing_file)
                logger.info(f"✅ Step 5 Completed: Found existing embeddings with {len(df)} chunks at {existing_file}")
                return True
                
            # Check for chunks file in multiple locations
            possible_chunks_paths = [
                "csv_dataframes/processed/chunked_pages.csv",
                self.base_dir / "csv_dataframes/processed/chunked_pages.csv",
                Path("csv_dataframes/processed/chunked_pages.csv").absolute()
            ]
            
            chunks_file = None
            for path in possible_chunks_paths:
                if Path(path).exists():
                    chunks_file = path
                    logger.info(f"📋 Found chunks file at: {path}")
                    break
                    
            if not chunks_file:
                logger.error(f"❌ Chunks file not found in any location:")
                for path in possible_chunks_paths:
                    logger.error(f"   - {path} (exists: {Path(path).exists()})")
                return False
                
            # Try to import embedding services with better error handling
            try:
                logger.info("🔄 Importing embedding services...")
                from ai_services.embedding_generator import embed_chunks_with_openai
                from ai_services.openai_services import client
                logger.info("✅ Successfully imported embedding services")
            except ImportError as ie:
                logger.error(f"❌ Failed to import ai_services: {ie}")
                logger.error("Make sure ai_services module exists and is properly structured")
                return False
            except Exception as e:
                logger.error(f"❌ Error importing ai_services: {e}")
                return False
            
            # Load chunks
            import pandas as pd
            chunks_df = pd.read_csv(chunks_file)
            logger.info(f"📋 Loaded {len(chunks_df)} chunks for embedding generation")
            
            # Check if we have OpenAI API key
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                logger.error("❌ OPENAI_API_KEY not found in environment variables")
                logger.error("Make sure your .env file contains OPENAI_API_KEY=your_key_here")
                return False
            
            # Generate embeddings
            logger.info("🤖 Starting embedding generation with OpenAI...")
            embedded_df = embed_chunks_with_openai(chunks_df, client)
            
            # Create output directory and save to first possible location
            output_path = possible_output_paths[0]  # Use relative path
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            embedded_df.to_csv(output_path, index=False)
            
            logger.info(f"✅ Step 5 Completed: Generated embeddings for {len(embedded_df)} chunks")
            logger.info(f"📁 Embeddings saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Step 5 Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_6_setup_vector_search(self):
        """Step 6: Setup vector search capabilities"""
        logger.info("🔍 Step 6: Setting up Vector Search...")
        try:
            # Check multiple possible locations for the embeddings file
            possible_paths = [
                "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                self.base_dir / "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                Path("csv_dataframes/embeddings/chunked_pages_with_embeddings.csv").absolute()
            ]
            
            # Find the embeddings file
            embeddings_file = None
            for path in possible_paths:
                if Path(path).exists():
                    embeddings_file = path
                    logger.info(f"📋 Found embeddings file at: {path}")
                    break
            
            if not embeddings_file:
                logger.error(f"❌ Embeddings file not found in any location:")
                for path in possible_paths:
                    logger.error(f"   - {path} (exists: {Path(path).exists()})")
                
                # Check if embedding generation actually completed
                logger.error("💡 This suggests Step 5 (Embedding Generation) may have failed silently")
                logger.error("💡 Or the embeddings file was saved to an unexpected location")
                
                # List files in embeddings directory to see what's there
                for path in possible_paths:
                    parent_dir = Path(path).parent
                    if parent_dir.exists():
                        files = list(parent_dir.glob("*.csv"))
                        logger.error(f"   Files in {parent_dir}: {[f.name for f in files]}")
                
                return False
                
            import pandas as pd
            import json
            
            df = pd.read_csv(embeddings_file)
            logger.info(f"📊 Loaded embeddings file with {len(df)} rows")
            
            # Check if the embeddings file has the expected columns
            required_columns = ['vectors']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"❌ Missing required columns in embeddings file: {missing_columns}")
                logger.error(f"Available columns: {list(df.columns)}")
                return False
            
            # Convert JSON string embeddings back to lists
            try:
                df['embedding_vectors'] = df['vectors'].apply(
                    lambda x: json.loads(x) if pd.notna(x) and x != 'None' else None
                )
                logger.info("✅ Successfully parsed embedding vectors from JSON")
            except Exception as e:
                logger.error(f"❌ Error parsing embedding vectors: {e}")
                return False
            
            # Filter out rows without embeddings
            df_with_embeddings = df[df['embedding_vectors'].notna()].copy()
            
            if len(df_with_embeddings) == 0:
                logger.error("❌ No valid embeddings found in the file")
                return False
            
            logger.info(f"✅ Step 6 Completed: Vector search ready with {len(df_with_embeddings)} chunks")
            
            # Show breakdown by content type if available
            if 'content_type' in df_with_embeddings.columns:
                content_type_breakdown = df_with_embeddings['content_type'].value_counts()
                logger.info(f"📊 Embedded content types: {dict(content_type_breakdown)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Step 6 Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_rag_system(self):
        """Test the RAG system with a sample query"""
        logger.info("\n🧪 Testing RAG System...")
        try:
            from ai_services.vector_search import vector_similarity_search, client
            from ai_services.openai_services import generate_response_with_context
            import pandas as pd
            import json
            
            embeddings_file = self.base_dir / "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
            if not embeddings_file.exists():
                logger.error(f"❌ Embeddings file not found: {embeddings_file}")
                return False
                
            df = pd.read_csv(embeddings_file)
            df['embedding_vectors'] = df['vectors'].apply(
                lambda x: json.loads(x) if pd.notna(x) and x != 'None' else None
            )
            df_with_embeddings = df[df['embedding_vectors'].notna()].copy()
            
            test_query = "What equipment is available for lithography?"
            logger.info(f"🔍 Test Query: '{test_query}'")
            
            retrieved_chunks = vector_similarity_search(test_query, df_with_embeddings, client, k=3)
            
            if retrieved_chunks:
                response, sources = generate_response_with_context(test_query, retrieved_chunks, client)
                logger.info(f"✅ RAG System Test Successful!")
                logger.info(f"📝 Response: {response[:200]}...")
                logger.info(f"📚 Sources: {len(sources)} documents")
                
                print(f"\n🔍 Sample Query: {test_query}")
                print(f"🤖 Response: {response}")
                print(f"📚 Sources: {len(sources)} documents found")
                
            else:
                logger.warning("⚠️ No relevant chunks found for test query")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ RAG System Test Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_processing_pipeline(self):
        """Run the processing pipeline for existing data"""
        logger.info("🚀 Starting Nanofab RAG Processing Pipeline...")
        start_time = time.time()
        
        # First check what data already exists
        existing_data = self.check_existing_data()
        
        pipeline_steps = [
            ("Wiki Text Processing", self.step_1_extract_wiki_texts),
            ("Wiki Table Processing", self.step_2_extract_wiki_tables), 
            ("Wiki Image Processing", self.step_3_extract_wiki_images),
            ("Document Chunking", self.step_4_chunk_documents),
            ("Embedding Generation", self.step_5_generate_embeddings),
            ("Vector Search Setup", self.step_6_setup_vector_search)
        ]
        
        successful_steps = 0
        
        for step_name, step_function in pipeline_steps:
            logger.info(f"\n{'='*50}")
            logger.info(f"Executing: {step_name}")
            logger.info(f"{'='*50}")
            
            step_start = time.time()
            success = step_function()
            step_duration = time.time() - step_start
            
            if success:
                successful_steps += 1
                logger.info(f"✅ {step_name} completed in {step_duration:.2f} seconds")
            else:
                logger.error(f"❌ {step_name} failed after {step_duration:.2f} seconds")
                logger.error("Pipeline stopped due to failure. Check logs for details.")
                return False
                
        total_duration = time.time() - start_time
        logger.info(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"✅ All {successful_steps}/{len(pipeline_steps)} steps completed")
        logger.info(f"⏱️ Total execution time: {total_duration:.2f} seconds")
        logger.info(f"📊 Your RAG system is now ready for queries!")
        
        return True

def main():
    """Main function to run the processing pipeline"""
    print("🔬 Nanofab Knowledge Management RAG Pipeline")
    print("📋 Processing Existing Data → Chunking → Embeddings")
    print("=" * 60)
    
    pipeline = NanofabRAGPipeline()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-only":
        logger.info("Running in test-only mode...")
        pipeline.test_rag_system()
    else:
        success = pipeline.run_processing_pipeline()
        
        if success:
            pipeline.test_rag_system()
            
            print("\n" + "="*60)
            print("🎯 PIPELINE COMPLETE!")
            print("✅ Your RAG system is ready for queries")
            print("🔍 Test it with: python backend/main.py --test-only")
            print("🌐 Or use: streamlit run frontend/app.py")
            print("="*60)
        else:
            print("\n❌ Pipeline failed. Check logs for details.")
            sys.exit(1)

if __name__ == "__main__":
    main()