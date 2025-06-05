"""
Document processing service
"""

import os
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Document, DocumentAnalysis, User
from app.schemas.document import DocumentSearchRequest, DocumentSearchResponse, DocumentResponse
from app.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document processing and management"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def process_document_async(self, document_id: int, db: Session):
        """Process document asynchronously"""
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document not found: {document_id}")
                return
            
            # Update status to processing
            document.processing_status = "processing"
            db.commit()
            
            # Read document content
            content = await self._extract_text_content(document.file_path, document.file_type)
            
            # Perform AI analysis
            analyses = await self._perform_ai_analysis(content, document.file_type)
            
            # Save analysis results
            for analysis_type, results in analyses.items():
                db_analysis = DocumentAnalysis(
                    document_id=document.id,
                    analysis_type=analysis_type,
                    results=results["results"],
                    confidence=results.get("confidence", 0.0),
                    processing_time=results.get("processing_time", 0.0)
                )
                db.add(db_analysis)
            
            # Update document status
            document.processed = True
            document.processing_status = "completed"
            db.commit()
            
            logger.info(f"Document processed successfully: {document_id}")
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            # Update status to failed
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.processing_status = "failed"
                db.commit()
    
    async def _extract_text_content(self, file_path: str, file_type: str) -> str:
        """Extract text content from document"""
        try:
            if file_type == ".txt":
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_type == ".pdf":
                # PDF text extraction
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        return text
                except ImportError:
                    logger.warning("PyPDF2 not available, using basic text extraction")
                    return f"PDF content from {file_path}"
            
            elif file_type == ".docx":
                # DOCX text extraction
                try:
                    from docx import Document as DocxDocument
                    doc = DocxDocument(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    logger.warning("python-docx not available, using basic text extraction")
                    return f"DOCX content from {file_path}"
            
            elif file_type in [".csv", ".xlsx"]:
                # Spreadsheet content extraction
                try:
                    import pandas as pd
                    if file_type == ".csv":
                        df = pd.read_csv(file_path)
                    else:
                        df = pd.read_excel(file_path)
                    return df.to_string()
                except ImportError:
                    logger.warning("pandas not available, using basic text extraction")
                    return f"Spreadsheet content from {file_path}"
            
            else:
                # Fallback for unknown file types
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return f"Error extracting content from {file_path}"
    
    async def _perform_ai_analysis(self, content: str, file_type: str) -> Dict[str, Any]:
        """Perform AI analysis on document content"""
        analyses = {}
        
        try:
            # Sentiment analysis
            sentiment_result = await self.ai_service.analyze_sentiment(content)
            analyses["sentiment"] = {
                "results": sentiment_result,
                "confidence": sentiment_result.get("confidence", 0.0),
                "processing_time": 0.5
            }
            
            # Entity extraction
            entities_result = await self.ai_service.extract_entities(content)
            analyses["entity_extraction"] = {
                "results": entities_result,
                "confidence": 0.8,
                "processing_time": 0.3
            }
            
            # Document classification
            classification_result = await self.ai_service.classify_document(content, file_type)
            analyses["classification"] = {
                "results": classification_result,
                "confidence": classification_result.get("confidence", 0.0),
                "processing_time": 0.4
            }
            
            # Risk assessment
            risk_result = await self.ai_service.assess_document_risk(content)
            analyses["risk_assessment"] = {
                "results": risk_result,
                "confidence": risk_result.get("confidence", 0.0),
                "processing_time": 0.6
            }
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            analyses["error"] = {
                "results": {"error": str(e)},
                "confidence": 0.0,
                "processing_time": 0.0
            }
        
        return analyses
    
    async def search_documents(
        self, 
        search_request: DocumentSearchRequest, 
        current_user: User, 
        db: Session
    ) -> DocumentSearchResponse:
        """Search documents based on criteria"""
        query = db.query(Document)
        
        # Apply user permissions
        if current_user.role not in ["admin", "manager"]:
            query = query.filter(Document.uploaded_by == current_user.id)
        
        # Apply search filters
        if search_request.file_types:
            query = query.filter(Document.file_type.in_(search_request.file_types))
        
        if search_request.date_from:
            query = query.filter(Document.created_at >= search_request.date_from)
        
        if search_request.date_to:
            query = query.filter(Document.created_at <= search_request.date_to)
        
        # Text search in filename
        if search_request.query:
            query = query.filter(
                Document.original_filename.contains(search_request.query)
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        documents = query.limit(search_request.limit).all()
        
        return DocumentSearchResponse(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=1,
            per_page=search_request.limit
        )
    
    async def get_document_insights(self, document_id: int, db: Session) -> Dict[str, Any]:
        """Get AI insights for a document"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"error": "Document not found"}
        
        # Get all analyses for the document
        analyses = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == document_id
        ).all()
        
        insights = {
            "document_info": {
                "filename": document.original_filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "processed": document.processed,
                "processing_status": document.processing_status
            },
            "analyses": {}
        }
        
        for analysis in analyses:
            insights["analyses"][analysis.analysis_type] = {
                "results": analysis.results,
                "confidence": analysis.confidence,
                "processing_time": analysis.processing_time,
                "created_at": analysis.created_at.isoformat()
            }
        
        return insights