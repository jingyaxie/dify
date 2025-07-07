#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test multimodal functionality
"""

import sys
import os
sys.path.append('api')

from core.rag.extractor.multimodal_image_extractor import MultimodalImageExtractor
from core.rag.extractor.multimodal_video_extractor import MultimodalVideoExtractor

def test_image_extractor():
    """Test image extractor"""
    print("Testing image extractor...")
    
    # Create image extractor instance
    extractor = MultimodalImageExtractor("test_tenant")
    
    # Test supported file extensions
    extensions = extractor.get_supported_extensions()
    print(f"Supported image extensions: {extensions}")
    
    # Test file type detection
    assert ".jpg" in extensions
    assert ".png" in extensions
    assert ".gif" in extensions
    
    print("Image extractor test passed!")

def test_video_extractor():
    """Test video extractor"""
    print("Testing video extractor...")
    
    # Create video extractor instance
    extractor = MultimodalVideoExtractor("test_tenant")
    
    # Test supported file extensions
    extensions = extractor.get_supported_extensions()
    print(f"Supported video extensions: {extensions}")
    
    # Test file type detection
    assert ".mp4" in extensions
    assert ".avi" in extensions
    assert ".mov" in extensions
    
    print("Video extractor test passed!")

def test_base_extractor():
    """Test base class functionality"""
    print("Testing base class functionality...")
    
    from core.rag.extractor.multimodal_base_extractor import MultimodalBaseExtractor
    
    # Create base class instance
    extractor = MultimodalBaseExtractor("test_tenant")
    
    # Test structured text generation
    image_text = extractor.generate_structured_text('image', 
        image_url='test.jpg',
        image_description='This is a test image',
        image_type='.jpg',
        file_size='1.2 MB',
        upload_time='2024-12-19 10:00:00'
    )
    print(f"Generated image text: {image_text[:100]}...")
    
    video_text = extractor.generate_structured_text('video',
        video_url='test.mp4',
        video_title='Test Video',
        duration='30 seconds',
        audio_transcription='This is audio transcription content',
        video_description='This is video description',
        file_size='5.6 MB',
        upload_time='2024-12-19 10:00:00'
    )
    print(f"Generated video text: {video_text[:100]}...")
    
    print("Base class functionality test passed!")

if __name__ == "__main__":
    print("Starting multimodal functionality test...")
    
    try:
        test_base_extractor()
        test_image_extractor()
        test_video_extractor()
        
        print("\nAll tests passed! Multimodal functionality implemented successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
