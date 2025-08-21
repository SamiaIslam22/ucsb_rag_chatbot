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
        
    def step_1_extract_wiki_texts(self):
        """Step 1: Extract text content from wiki pages"""
        logger.info("🚀 Step 1: Starting Wiki Text Extraction...")
        try:
            output_file = self.base_dir / "csv_dataframes/raw/wiki_texts.csv"
            if output_file.exists():
                logger.info(f"Found existing {output_file}, skipping extraction...")
                return True
                
            # Import and run wiki_texts extraction
            from extraction.wiki_texts import run_all_scrapes, wiki_links
            import pandas as pd
            
            # Run the scraping
            scraped_data = asyncio.run(run_all_scrapes(wiki_links))
            
            # Save the data
            df = pd.DataFrame(scraped_data)
            df.to_csv(output_file, index=False)
            
            logger.info("✅ Step 1 Completed: Wiki texts extracted successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Step 1 Failed: Wiki text extraction failed: {e}")
            return False

    def step_2_extract_wiki_tables(self):
        """Step 2: Extract tables from wiki pages"""
        logger.info("🚀 Step 2: Starting Wiki Table Extraction...")
        try:
            output_file = self.base_dir / "csv_dataframes/raw/wiki_tables.csv"
            if output_file.exists():
                logger.info(f"Found existing {output_file}, skipping extraction...")
                return True
                
            # Import and run table extraction
            from extraction import wiki_table
            
            # The wiki_table module should run its main logic when imported
            # and save to the correct output path
            
            logger.info("✅ Step 2 Completed: Wiki tables extracted successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Step 2 Failed: Wiki table extraction failed: {e}")
            return False

    def step_3_extract_wiki_images(self):
        """Step 3: Extract and process images from wiki pages"""
        logger.info("🚀 Step 3: Starting Wiki Image Extraction...")
        try:
            output_file = self.base_dir / "csv_dataframes/raw/wiki_images.csv"
            if output_file.exists():
                logger.info(f"Found existing {output_file}, skipping extraction...")
                return True
                
            # Import and run image extraction
            from extraction.wiki_images import main as wiki_images_main
            
            asyncio.run(wiki_images_main())
            
            logger.info("✅ Step 3 Completed: Wiki images processed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Step 3 Failed: Wiki image extraction failed: {e}")
            return False

    def step_4_chunk_documents(self):
        """Step 4: Chunk all extracted documents"""
        logger.info("🚀 Step 4: Starting Document Chunking...")
        try:
            output_file = self.base_dir / "csv_dataframes/processed/chunked_pages.csv"
            
            # Check if file already exists
            if output_file.exists():
                logger.info(f"Found existing {output_file}, skipping chunking...")
                return True
            
            # Import chunking module - it will run automatically
            try:
                import chunking.chunking
                # Give it a moment to complete
                time.sleep(1)
            except ImportError as ie:
                logger.error(f"Could not import chunking module: {ie}")
                return False
            
            # Check if the output file was created
            if output_file.exists():
                logger.info("✅ Step 4 Completed: Documents chunked successfully")
                return True
            else:
                logger.error("❌ Chunking process ran but output file not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Step 4 Failed: Document chunking failed: {e}")
            return False

    def step_5_generate_embeddings(self):
        """Step 5: Generate embeddings for all chunks"""
        logger.info("🚀 Step 5: Starting Embedding Generation...")
        try:
            output_file = self.base_dir / "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
            if output_file.exists():
                logger.info(f"Found existing {output_file}, skipping embedding generation...")
                return True
                
            # Import and run embedding generation
            from ai_services.embedding_generator import embed_chunks_with_openai
            from ai_services.openai_services import client
            import pandas as pd
            
            # Load chunked data
            chunks_file = self.base_dir / "csv_dataframes/processed/chunked_pages.csv"
            chunks_df = pd.read_csv(chunks_file)
            
            # Generate embeddings
            embedded_df = embed_chunks_with_openai(chunks_df, client)
            
            # Save embeddings
            embedded_df.to_csv(output_file, index=False)
            
            logger.info("✅ Step 5 Completed: Embeddings generated successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Step 5 Failed: Embedding generation failed: {e}")
            return False

    def step_6_setup_vector_search(self):
        """Step 6: Setup vector search capabilities"""
        logger.info("🚀 Step 6: Setting up Vector Search...")
        try:
            # Load the embedded data to verify everything works
            embeddings_file = self.base_dir / "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
            
            if not embeddings_file.exists():
                logger.error(f"Embeddings file {embeddings_file} not found!")
                return False
                
            import pandas as pd
            import json
            
            df = pd.read_csv(embeddings_file)
            
            # Convert JSON string embeddings back to lists
            df['embedding_vectors'] = df['vectors'].apply(
                lambda x: json.loads(x) if pd.notna(x) and x != 'None' else None
            )
            
            # Filter out rows without embeddings
            df_with_embeddings = df[df['embedding_vectors'].notna()].copy()
            
            logger.info(f"✅ Step 6 Completed: Vector search ready with {len(df_with_embeddings)} chunks")
            return True
        except Exception as e:
            logger.error(f"❌ Step 6 Failed: Vector search setup failed: {e}")
            return False

    def test_rag_system(self):
        """Test the RAG system with a sample query"""
        logger.info("\n🧪 Testing RAG System...")
        try:
            from ai_services.vector_search import vector_similarity_search, client
            from ai_services.openai_services import generate_response_with_context
            import pandas as pd
            import json
            
            # Load the data
            embeddings_file = self.base_dir / "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
            if not embeddings_file.exists():
                logger.error(f"Embeddings file {embeddings_file} not found!")
                return False
                
            df = pd.read_csv(embeddings_file)
            df['embedding_vectors'] = df['vectors'].apply(
                lambda x: json.loads(x) if pd.notna(x) and x != 'None' else None
            )
            df_with_embeddings = df[df['embedding_vectors'].notna()].copy()
            
            # Test query
            test_query = "What equipment is available for lithography?"
            logger.info(f"Test Query: '{test_query}'")
            
            # Search for relevant chunks
            retrieved_chunks = vector_similarity_search(test_query, df_with_embeddings, client, k=3)
            
            if retrieved_chunks:
                # Generate response
                response, sources = generate_response_with_context(test_query, retrieved_chunks, client)
                logger.info(f"✅ RAG System Test Successful!")
                logger.info(f"Response: {response[:200]}...")
                logger.info(f"Sources found: {len(sources)}")
                
                # Print sample response for verification
                print(f"\n🔍 Sample Query: {test_query}")
                print(f"📝 Response: {response}")
                print(f"📚 Sources: {len(sources)} documents found")
                
            else:
                logger.warning("⚠️ No relevant chunks found for test query")
                
            return True
        except Exception as e:
            logger.error(f"❌ RAG System Test Failed: {e}")
            return False

    def run_complete_pipeline(self):
        """Run the complete RAG pipeline"""
        logger.info("🎯 Starting Complete Nanofab RAG Pipeline...")
        start_time = time.time()
        
        pipeline_steps = [
            ("Wiki Text Extraction", self.step_1_extract_wiki_texts),
            ("Wiki Table Extraction", self.step_2_extract_wiki_tables), 
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
        logger.info(f"⏱️  Total execution time: {total_duration:.2f} seconds")
        logger.info(f"📊 Your RAG system is now ready for queries!")
        
        return True

def main():
    """Main function to run the complete pipeline"""
    print("🔬 Nanofab Knowledge Management RAG Pipeline")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = NanofabRAGPipeline()
    
    # Check if we should run the full pipeline or just test
    if len(sys.argv) > 1 and sys.argv[1] == "--test-only":
        logger.info("Running in test-only mode...")
        pipeline.test_rag_system()
    else:
        # Run complete pipeline
        success = pipeline.run_complete_pipeline()
        
        if success:
            # Test the system
            pipeline.test_rag_system()
            
            print("\n" + "="*60)
            print("🎯 NEXT STEPS:")
            print("1. Your RAG system is ready!")
            print("2. Run queries using the vector_search and openai_services modules")
            print("3. Check the generated files in csv_dataframes/")
            print("4. Use the frontend/app.py for a web interface")
            print("="*60)
        else:
            print("\n❌ Pipeline failed. Check logs for details.")
            sys.exit(1)

if __name__ == "__main__":
    main()