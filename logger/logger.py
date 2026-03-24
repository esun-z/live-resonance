"""
日志配置模块
提供统一的日志格式和输出配置
"""

import logging
import sys
from typing import Optional


def setup_logging_console(level: int = logging.INFO, 
                  log_file: Optional[str] = None,
                  console_format: Optional[str] = None,
                  file_format: Optional[str] = None) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径，如果为None则只输出到控制台
        console_format: 控制台输出格式
        file_format: 文件输出格式
    
    Returns:
        根日志记录器
    """
    
    # 默认格式
    if console_format is None:
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if file_format is None:
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 创建控制台格式化器
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    
    # 添加控制台处理器
    root_logger.addHandler(console_handler)
    
    # 如果指定了日志文件，创建文件处理器
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            
            # 创建文件格式化器
            file_formatter = logging.Formatter(file_format)
            file_handler.setFormatter(file_formatter)
            
            # 添加文件处理器
            root_logger.addHandler(file_handler)
            
            logging.info(f"日志文件已启用: {log_file}")
        except Exception as e:
            logging.error(f"无法创建日志文件 {log_file}: {e}")
    
    logging.info("日志系统初始化完成")
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)


# 预定义的日志格式
FORMATS = {
    'simple': '%(levelname)s - %(message)s',
    'detailed': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    'timestamp': '%(asctime)s - %(message)s',
    'debug': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
}


if __name__ == "__main__":
    # 测试日志配置
    setup_logging_console(logging.DEBUG)
    
    logger = get_logger(__name__)
    
    logger.debug("这是DEBUG级别的消息")
    logger.info("这是INFO级别的消息")
    logger.warning("这是WARNING级别的消息")
    logger.error("这是ERROR级别的消息")
    logger.critical("这是CRITICAL级别的消息")