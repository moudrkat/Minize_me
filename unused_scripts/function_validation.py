import numpy as np # linear algebra
import sympy as sp
from sympy import symbols, diff, lambdify
import streamlit as st


# Function to check if the symbolic derivatives exist for all variables
def check_symbolic_differentiability(f, variables):
    try:
        # Try computing the symbolic derivative for all variables
        derivatives = [sp.diff(f, var) for var in variables]
        st.write("Symbolic differentiation check done!")
        return True, derivatives
    except Exception as e:
        st.write(f"Error during symbolic differentiation: {e}")
        return False, None
import math

def check_for_numerical_instability(f, x_vals, y_vals):
    # Ensure the symbols used in f are 'x' and 'y'
    x, y = sp.symbols('x y')
    for xi in x_vals:
        for yi in y_vals:
            try:
                # Try evaluating the function at each point (xi, yi)
                value = f.subs({x: xi, y: yi}).evalf()  # Evaluate symbolically to a floating point number 
                # Check if the value is NaN or Inf using Python's math functions
                if math.isnan(value) or math.isinf(value):
                    return False, f"Function evaluation resulted in NaN or Inf at point ({xi}, {yi})."
                # Check gradients numerically at the same point
                grad_x, grad_y = numerical_gradient(f, xi, yi, x, y)  # Pass xi, yi for numeric gradient
                if math.isnan(grad_x) or math.isnan(grad_y) or math.isinf(grad_x) or math.isinf(grad_y):
                    return False, f"Gradients resulted in NaN or Inf at point ({xi}, {yi})."
            except Exception as e:
                return False, f"Error at point ({xi}, {yi}): {str(e)}"
    st.write("Numerical stability check done for all sampled points!")
    return True, None

def numerical_gradient(f, xi, yi, x, y, epsilon=1e-5):
    # Compute gradients using finite differences
    f_x = f.subs(x, xi + epsilon).subs(y, yi) - f.subs(x, xi - epsilon).subs(y, yi)
    f_y = f.subs(x, xi).subs(y, yi + epsilon) - f.subs(x, xi).subs(y, yi - epsilon)
    grad_x = f_x / (2 * epsilon)
    grad_y = f_y / (2 * epsilon)
    # Convert gradients to floats and check for NaN or Inf
    grad_x = grad_x.evalf()
    grad_y = grad_y.evalf()
    return grad_x, grad_y

# Function to check for vanishing or exploding gradients
def check_for_vanishing_exploding_gradients(f, x_vals, y_vals, x, y, gradient_threshold=1e10, vanishing_threshold=1e-5, min_threshold=1e-3):
    for x_val in x_vals:
        for y_val in y_vals:
            # Compute the numerical gradients at each point
            grad_x, grad_y = numerical_gradient(f, x_val, y_val, x, y)  
            # Convert gradients to floats
            grad_x = float(grad_x)
            grad_y = float(grad_y)  
            # Check for exploding gradients (if gradients are too large)
            if np.abs(grad_x) > gradient_threshold or np.abs(grad_y) > gradient_threshold:
                return False, f"Exploding gradients at point ({x_val}, {y_val}) with gradients ({grad_x}, {grad_y})."
            # Allow vanishing gradients if they are near the minimum (i.e., if gradients are below a small threshold)
            if np.abs(grad_x) < vanishing_threshold and np.abs(grad_y) < vanishing_threshold:
                if np.abs(grad_x) > min_threshold or np.abs(grad_y) > min_threshold:
                    return False, f"Vanishing gradients at point ({x_val}, {y_val}) with gradients ({grad_x}, {grad_y})."
    st.write("Vanishing/Exploding gradient check done!")
    return True, None

# Check if function values at extreme points cause overflow/underflow
def check_for_large_inputs(f, x_vals, y_vals):
    x, y = sp.symbols('x y')
    for xi in x_vals:
        for yi in y_vals:
            try:
                value = f.subs({x: xi, y: yi}).evalf()
                if math.isnan(value) or math.isinf(value):
                    return False, f"Overflow or underflow at point ({xi}, {yi})."
            except Exception as e:
                return False, f"Error at point ({xi}, {yi}): {str(e)}"
    st.write("Large input check passed!")
    return True, None

# Main function to validate the given function for optimization
def validate_function_for_optimization(f, variables):
    # 1. Check if the function is symbolically differentiable
    differentiable, derivatives = check_symbolic_differentiability(f, variables)
    if not differentiable:
        st.write("Function is not differentiable!")
        return False
    # 2. Check if the function and its gradients are numerically stable
    x_vals = np.linspace(-5, 5, 50)  # 5 points between -10 and 10 for x
    y_vals = np.linspace(-5, 5, 50)  # 5 points between -10 and 10 for y
    stable, error_message = check_for_numerical_instability(f, x_vals, y_vals)
    if not stable:
        st.write(f"Numerical instability detected: {error_message}")
        return False
    # 3. Check for large input values
    large_input_check, large_input_message = check_for_large_inputs(f, x_vals, y_vals)
    if not large_input_check:
        st.write(f"Large input issue detected: {large_input_message}")
        return False
    # 4. Check for vanishing or exploding gradients
    gradient_check, gradient_message = check_for_vanishing_exploding_gradients(f, x_vals, y_vals, x, y)
    if not gradient_check:
        st.write(f"Vanishing/Exploding gradient issue detected: {gradient_message}")
        return False
    # If all checks pass, we return True indicating the function is valid for optimization
    st.write("Function is valid for optimization!")
    return True
