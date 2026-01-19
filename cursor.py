async def inject_cursor_styles(page):
    """Inject custom cursor styles using system cursors"""
    await page.evaluate("""
        () => {
            // Remove existing cursor if any
            const existingCursor = document.getElementById('custom-cursor');
            if (existingCursor) existingCursor.remove();
            
            // Create cursor element - this will show actual cursor shape
            const cursor = document.createElement('div');
            cursor.id = 'custom-cursor';
            cursor.style.cssText = `
                position: fixed;
                width: 32px;
                height: 32px;
                pointer-events: none;
                z-index: 999999;
                transition: all 0.15s ease;
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
            `;
            
            // Default arrow cursor SVG
            cursor.style.backgroundImage = `url('data:image/svg+xml;utf8,<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 94.85 122.88" style="enable-background:new 0 0 94.85 122.88" xml:space="preserve"><g><path d="M60.56,122.49c-1.63,0.83-3.68,0.29-4.56-1.22L38.48,91.1l-17.38,19.51c-5.24,5.88-12.16,7.34-12.85-1.57L0,1.59h0 C-0.04,1.03,0.2,0.46,0.65,0.13C1.17-0.1,1.78-0.02,2.24,0.3l0,0l88.92,60.87c7.37,5.05,2.65,10.31-5.06,11.91l-25.58,5.3 l17.37,30.26c0.86,1.51,0.31,3.56-1.22,4.55L60.56,122.49L60.56,122.49L60.56,122.49z"/></g></svg>')`;
            cursor.style.transform = 'translate(0, 0)';
            
            document.body.appendChild(cursor);
            
            // Hide default cursor
            const style = document.createElement('style');
            style.id = 'custom-cursor-style';
            style.textContent = `
                * {
                    cursor: none !important;
                }
            `;
            document.head.appendChild(style);
            
            window.customCursorPosition = { x: 0, y: 0 };
            window.customCursorMode = 'arrow';
        }
    """)

async def set_cursor_mode(page, mode='arrow'):
    """Set cursor mode: 'arrow' or 'pointer' (hand)"""
    await page.evaluate(f"""
        (mode) => {{
            const cursor = document.getElementById('custom-cursor');
            window.customCursorMode = mode;
            
            if (cursor) {{
                if (mode === 'pointer') {{
                    // Hand/Pointer cursor SVG
                    cursor.style.backgroundImage = `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-hand-index-thumb" viewBox="0 0 16 16">
                    <path d="M6.75 1a.75.75 0 0 1 .75.75V8a.5.5 0 0 0 1 0V5.467l.086-.004c.317-.012.637-.008.816.027.134.027.294.096.448.182.077.042.15.147.15.314V8a.5.5 0 0 0 1 0V6.435l.106-.01c.316-.024.584-.01.708.04.118.046.3.207.486.43.081.096.15.19.2.259V8.5a.5.5 0 1 0 1 0v-1h.342a1 1 0 0 1 .995 1.1l-.271 2.715a2.5 2.5 0 0 1-.317.991l-1.395 2.442a.5.5 0 0 1-.434.252H6.118a.5.5 0 0 1-.447-.276l-1.232-2.465-2.512-4.185a.517.517 0 0 1 .809-.631l2.41 2.41A.5.5 0 0 0 6 9.5V1.75A.75.75 0 0 1 6.75 1M8.5 4.466V1.75a1.75 1.75 0 1 0-3.5 0v6.543L3.443 6.736A1.517 1.517 0 0 0 1.07 8.588l2.491 4.153 1.215 2.43A1.5 1.5 0 0 0 6.118 16h6.302a1.5 1.5 0 0 0 1.302-.756l1.395-2.441a3.5 3.5 0 0 0 .444-1.389l.271-2.715a2 2 0 0 0-1.99-2.199h-.581a5 5 0 0 0-.195-.248c-.191-.229-.51-.568-.88-.716-.364-.146-.846-.132-1.158-.108l-.132.012a1.26 1.26 0 0 0-.56-.642 2.6 2.6 0 0 0-.738-.288c-.31-.062-.739-.058-1.05-.046zm2.094 2.025"/>
                    </svg>')`;
                    cursor.style.width = '24px';
                    cursor.style.height = '24px';
                }} else {{
                    // Arrow cursor SVG
                    cursor.style.backgroundImage = `url('data:image/svg+xml;utf8,<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 94.85 122.88" style="enable-background:new 0 0 94.85 122.88" xml:space="preserve"><g><path d="M60.56,122.49c-1.63,0.83-3.68,0.29-4.56-1.22L38.48,91.1l-17.38,19.51c-5.24,5.88-12.16,7.34-12.85-1.57L0,1.59h0 C-0.04,1.03,0.2,0.46,0.65,0.13C1.17-0.1,1.78-0.02,2.24,0.3l0,0l88.92,60.87c7.37,5.05,2.65,10.31-5.06,11.91l-25.58,5.3 l17.37,30.26c0.86,1.51,0.31,3.56-1.22,4.55L60.56,122.49L60.56,122.49L60.56,122.49z"/></g></svg>')`;
                    cursor.style.width = '24px';
                    cursor.style.height = '24px';
                }}
            }}
        }}
    """, mode)

async def move_cursor_to(page, x, y, duration=500):
    """Smoothly move cursor to position"""
    await page.evaluate(f"""
        ({{x, y, duration}}) => {{
            const cursor = document.getElementById('custom-cursor');
            
            if (cursor) {{
                cursor.style.left = x + 'px';
                cursor.style.top = y + 'px';
                cursor.style.transition = `all ${{duration}}ms ease-out`;
            }}
            
            window.customCursorPosition = {{ x, y }};
        }}
    """, {"x": x, "y": y, "duration": duration})
    await page.wait_for_timeout(duration)

async def move_mouse_realtime(page, x, y):
    """Move the actual mouse cursor to position"""
    await page.mouse.move(x, y)

async def click_with_cursor(page, selector, delay=100):
    """Move cursor to element and click with hand cursor animation"""
    # Get element position
    element = await page.query_selector(selector)
    if not element:
        return
    
    box = await element.bounding_box()
    if not box:
        return
    
    center_x = box['x'] + box['width'] / 2
    center_y = box['y'] + box['height'] / 2
    
    # Move visual cursor to element
    await move_cursor_to(page, center_x, center_y, duration=800)
    
    # Move actual mouse cursor
    await move_mouse_realtime(page, center_x, center_y)
    
    # Change to hand cursor
    await set_cursor_mode(page, 'pointer')
    await page.wait_for_timeout(300)
    
    # Click animation - make cursor smaller
    await page.evaluate("""
        () => {
            const cursor = document.getElementById('custom-cursor');
            if (cursor) {
                const originalTransform = cursor.style.transform;
                cursor.style.transform = 'translate(-50%, -50%) scale(0.7)';
                setTimeout(() => {
                    cursor.style.transform = originalTransform;
                }, 150);
            }
        }
    """)
    
    # Actual click
    await page.click(selector)
    await page.wait_for_timeout(delay)
    
    # Back to arrow cursor
    await set_cursor_mode(page, 'arrow')

async def type_with_cursor(page, selector, text, delay=80):
    """Move cursor to input and type with cursor indication"""
    element = await page.query_selector(selector)
    if not element:
        return
    
    box = await element.bounding_box()
    if not box:
        return
    
    center_x = box['x'] + box['width'] / 2
    center_y = box['y'] + box['height'] / 2
    
    # Move visual cursor to input
    await move_cursor_to(page, center_x, center_y, duration=600)
    
    # Move actual mouse
    await move_mouse_realtime(page, center_x, center_y)
    
    # Change to hand cursor
    await set_cursor_mode(page, 'pointer')
    await page.wait_for_timeout(200)
    
    # Click and type
    await page.click(selector)
    
    # Back to arrow for typing
    await set_cursor_mode(page, 'arrow')
    await page.type(selector, text, delay=delay)

async def hover_with_cursor(page, selector, duration=500):
    """Hover over element with cursor"""
    element = await page.query_selector(selector)
    if not element:
        return
    
    box = await element.bounding_box()
    if not box:
        return
    
    center_x = box['x'] + box['width'] / 2
    center_y = box['y'] + box['height'] / 2
    
    await move_cursor_to(page, center_x, center_y, duration=duration)
    await move_mouse_realtime(page, center_x, center_y)
    await set_cursor_mode(page, 'pointer')


async def hover_dropdown_option(page, option_selector, offset_y=0):
    """Hover over a specific dropdown option with cursor
    
    Args:
        page: Playwright page object
        option_selector: CSS selector for the option element
        offset_y: Vertical offset to adjust cursor position (default: 0)
    """
    # Wait for option to be visible
    await page.wait_for_selector(option_selector, state="visible")
    
    element = await page.query_selector(option_selector)
    if not element:
        return
    
    box = await element.bounding_box()
    if not box:
        return
    
    # Position cursor in the middle of the option
    center_x = box['x'] + box['width'] / 2
    center_y = box['y'] + box['height'] / 2 + offset_y
    
    # Move cursor to option
    await move_cursor_to(page, center_x, center_y, duration=600)
    await move_mouse_realtime(page, center_x, center_y)
    await set_cursor_mode(page, 'arrow')
    await page.wait_for_timeout(500)  # Pause to show the hover

async def select_option_with_cursor(page, dropdown_selector, option_text):
    """Click dropdown, hover over option, and select it
    
    Args:
        page: Playwright page object
        dropdown_selector: CSS selector for the dropdown
        option_text: Text of the option to select
    """
    # Click to open dropdown
    await click_with_cursor(page, dropdown_selector)
    await page.wait_for_timeout(500)
    
    # Hover over the option (this shows cursor above it)
    option_selector = f'{dropdown_selector}'
    await hover_dropdown_option(page, option_selector)
    
    # Select the option
    await page.select_option(dropdown_selector, label=option_text)
    await set_cursor_mode(page, 'arrow')


async def scroll_with_cursor(page, direction='down', amount=None, duration=1000, container_selector=None):
    """Scroll the page or a specific container with cursor indication
    
    Args:
        page: Playwright page object
        direction: 'down', 'up', 'bottom', or 'top'
        amount: Pixels to scroll (None for full scroll)
        duration: Animation duration in milliseconds
        container_selector: CSS selector for scrollable container (None for window scroll)
    """
    try:
        # Calculate target scroll position
        target_scroll = await page.evaluate("""
            (params) => {
                const direction = params.direction;
                const amount = params.amount;
                const containerSelector = params.containerSelector;
                
                let scrollElement;
                let currentScroll;
                let maxScroll;
                
                if (containerSelector) {
                    // Scroll inside a specific container
                    scrollElement = document.querySelector(containerSelector);
                    if (!scrollElement) {
                        console.error('Container not found:', containerSelector);
                        return null;
                    }
                    currentScroll = scrollElement.scrollTop;
                    maxScroll = scrollElement.scrollHeight - scrollElement.clientHeight;
                } else {
                    // Scroll the window
                    scrollElement = null;
                    currentScroll = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
                    maxScroll = Math.max(
                        document.body.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.clientHeight,
                        document.documentElement.scrollHeight,
                        document.documentElement.offsetHeight
                    ) - window.innerHeight;
                }
                
                let target = currentScroll;
                
                if (direction === 'bottom') {
                    target = maxScroll;
                } else if (direction === 'top') {
                    target = 0;
                } else if (direction === 'down') {
                    target = amount ? Math.min(currentScroll + amount, maxScroll) : Math.min(currentScroll + 500, maxScroll);
                } else if (direction === 'up') {
                    target = amount ? Math.max(0, currentScroll - amount) : Math.max(0, currentScroll - 500);
                }
                
                return {
                    target: target,
                    isContainer: !!containerSelector
                };
            }
        """, {"direction": direction, "amount": amount, "containerSelector": container_selector})
        
        if target_scroll is None or target_scroll.get('target') is None:
            print("Could not calculate scroll target")
            return
        
        # Perform smooth scroll with better animation
        await page.evaluate("""
            (params) => {
                return new Promise((resolve) => {
                    const targetScroll = params.target;
                    const duration = params.duration;
                    const containerSelector = params.containerSelector;
                    const isContainer = params.isContainer;
                    
                    let scrollElement;
                    let startScroll;
                    
                    if (isContainer && containerSelector) {
                        scrollElement = document.querySelector(containerSelector);
                        if (!scrollElement) {
                            resolve();
                            return;
                        }
                        startScroll = scrollElement.scrollTop;
                    } else {
                        scrollElement = null;
                        startScroll = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
                    }
                    
                    const distance = targetScroll - startScroll;
                    
                    if (Math.abs(distance) < 1) {
                        resolve();
                        return;
                    }
                    
                    let startTime = null;
                    
                    function animation(currentTime) {
                        if (startTime === null) startTime = currentTime;
                        const timeElapsed = currentTime - startTime;
                        const progress = Math.min(timeElapsed / duration, 1);
                        
                        // Ease in-out cubic function
                        const ease = progress < 0.5
                            ? 4 * progress * progress * progress
                            : 1 - Math.pow(-2 * progress + 2, 3) / 2;
                        
                        const newPosition = startScroll + distance * ease;
                        
                        if (scrollElement) {
                            scrollElement.scrollTop = newPosition;
                        } else {
                            window.scrollTo(0, newPosition);
                        }
                        
                        if (progress < 1) {
                            requestAnimationFrame(animation);
                        } else {
                            // Ensure final position
                            if (scrollElement) {
                                scrollElement.scrollTop = targetScroll;
                            } else {
                                window.scrollTo(0, targetScroll);
                            }
                            resolve();
                        }
                    }
                    
                    requestAnimationFrame(animation);
                });
            }
        """, {
            "target": target_scroll['target'], 
            "duration": duration, 
            "containerSelector": container_selector,
            "isContainer": target_scroll.get('isContainer', False)
        })
        
        await page.wait_for_timeout(100)
        
    except Exception as e:
        print(f"Scroll error: {e}")
        # Fallback to instant scroll
        if container_selector:
            if direction == 'bottom':
                await page.evaluate(f"document.querySelector('{container_selector}').scrollTop = document.querySelector('{container_selector}').scrollHeight")
            elif direction == 'top':
                await page.evaluate(f"document.querySelector('{container_selector}').scrollTop = 0")
        else:
            if direction == 'bottom':
                await page.evaluate("window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight))")
            elif direction == 'top':
                await page.evaluate("window.scrollTo(0, 0)")

async def scroll_to_element_with_cursor(page, selector, offset=0, duration=1000, container_selector=None):
    """Scroll to bring an element into view with cursor tracking
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        offset: Additional offset from element position
        duration: Animation duration in milliseconds
        container_selector: CSS selector for scrollable container (None for window scroll)
    """
    try:
        # Wait for element
        await page.wait_for_selector(selector, timeout=5000)
        
        # Scroll to element with animation
        await page.evaluate("""
            (params) => {
                return new Promise((resolve) => {
                    const element = document.querySelector(params.selector);
                    if (!element) {
                        console.log('Element not found:', params.selector);
                        resolve();
                        return;
                    }
                    
                    const duration = params.duration;
                    const offset = params.offset;
                    const containerSelector = params.containerSelector;
                    
                    let scrollElement;
                    let startScroll;
                    let containerHeight;
                    let elementTop;
                    
                    if (containerSelector) {
                        // Scroll within container
                        scrollElement = document.querySelector(containerSelector);
                        if (!scrollElement) {
                            resolve();
                            return;
                        }
                        
                        startScroll = scrollElement.scrollTop;
                        containerHeight = scrollElement.clientHeight;
                        
                        // Get element position relative to container
                        const containerRect = scrollElement.getBoundingClientRect();
                        const elementRect = element.getBoundingClientRect();
                        elementTop = elementRect.top - containerRect.top + startScroll;
                    } else {
                        // Scroll the window
                        scrollElement = null;
                        startScroll = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
                        containerHeight = window.innerHeight;
                        
                        const elementRect = element.getBoundingClientRect();
                        elementTop = elementRect.top + startScroll;
                    }
                    
                    // Calculate target position (center element in viewport)
                    const elementHeight = element.offsetHeight;
                    const targetScroll = elementTop - (containerHeight / 2) + (elementHeight / 2) + offset;
                    
                    // Calculate max scroll
                    let maxScroll;
                    if (scrollElement) {
                        maxScroll = scrollElement.scrollHeight - scrollElement.clientHeight;
                    } else {
                        maxScroll = Math.max(
                            document.body.scrollHeight,
                            document.documentElement.scrollHeight
                        ) - containerHeight;
                    }
                    
                    const finalTarget = Math.max(0, Math.min(targetScroll, maxScroll));
                    const distance = finalTarget - startScroll;
                    
                    if (Math.abs(distance) < 1) {
                        resolve();
                        return;
                    }
                    
                    let startTime = null;
                    
                    function animation(currentTime) {
                        if (startTime === null) startTime = currentTime;
                        const timeElapsed = currentTime - startTime;
                        const progress = Math.min(timeElapsed / duration, 1);
                        
                        // Ease in-out cubic
                        const ease = progress < 0.5
                            ? 4 * progress * progress * progress
                            : 1 - Math.pow(-2 * progress + 2, 3) / 2;
                        
                        const newPosition = startScroll + distance * ease;
                        
                        if (scrollElement) {
                            scrollElement.scrollTop = newPosition;
                        } else {
                            window.scrollTo(0, newPosition);
                        }
                        
                        if (progress < 1) {
                            requestAnimationFrame(animation);
                        } else {
                            if (scrollElement) {
                                scrollElement.scrollTop = finalTarget;
                            } else {
                                window.scrollTo(0, finalTarget);
                            }
                            resolve();
                        }
                    }
                    
                    requestAnimationFrame(animation);
                });
            }
        """, {"selector": selector, "offset": offset, "duration": duration, "containerSelector": container_selector})
        
        await page.wait_for_timeout(100)
        
        # Move cursor to element after scroll
        element = await page.query_selector(selector)
        if element:
            box = await element.bounding_box()
            if box:
                center_x = box['x'] + box['width'] / 2
                center_y = box['y'] + box['height'] / 2
                await move_cursor_to(page, center_x, center_y, duration=500)
            
    except Exception as e:
        print(f"Scroll to element error: {e}")
        # Fallback
        try:
            if container_selector:
                await page.evaluate(f"""
                    const container = document.querySelector('{container_selector}');
                    const el = document.querySelector('{selector}');
                    if (container && el) {{
                        const containerRect = container.getBoundingClientRect();
                        const elRect = el.getBoundingClientRect();
                        const scrollTop = elRect.top - containerRect.top + container.scrollTop - container.clientHeight / 2;
                        container.scrollTo({{ top: scrollTop, behavior: 'smooth' }});
                    }}
                """)
            else:
                await page.evaluate(f"""
                    const el = document.querySelector('{selector}');
                    if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                """)
            await page.wait_for_timeout(1000)
        except:
            pass
