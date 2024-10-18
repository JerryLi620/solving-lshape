from sympy import isprime, primefactors
from sympy.ntheory.residue_ntheory import primitive_root


class PowerResidueColoring:
    def __init__(self, p, k, l):
        """
        Initializes the PowerResidueColoring instance.

        Parameters:
        - p: A prime number.
        - k: The number of color classes.
        - l: The length of progression to avoid.
        """
        if not isprime(p):
            raise ValueError("p must be a prime number.")
        self.p = p
        self.k = k
        self.l = l
        self.p_n = self.largest_prime_factor(p)
        self.r_n = self.find_primitive_root(p)
        self.sequence = []
        self.color_classes = {}
        self.expanded_classes = {}

    def largest_prime_factor(self, n):
        """
        Finds the largest prime factor of n.

        Parameters:
        - n: The number to factor.

        Returns:
        - The largest prime factor of n.
        """
        factors = primefactors(n)
        return max(factors)

    def find_primitive_root(self, n):
        """
        Finds a primitive root modulo n.

        Parameters:
        - n: A prime number.

        Returns:
        - A primitive root modulo n.
        """
        return primitive_root(n)

    def construct_sequence(self):
        """
        Constructs the sequence S_n based on the primitive root.

        Updates:
        - self.sequence: The constructed sequence.
        """
        self.sequence = [pow(self.r_n, i, self.p) for i in range(1, self.p_n)]

    def partition_into_color_classes(self):
        """
        Partitions the elements into k color classes.

        Updates:
        - self.color_classes: A dictionary with color class labels as keys and lists of elements as values.
        """
        self.color_classes = {f"C_{i+1}": [] for i in range(self.k)}
        for idx, elem in enumerate(self.sequence):
            class_label = f"C_{((idx+1) % self.k) + 1}"
            self.color_classes[class_label].append(elem)
            
        # Add p_n to C_k
        self.color_classes[f"C_{self.k}"].append(self.p_n)
        
    def expand_certificate(self):
        """
        Expands the certificate using the repetition property.

        The repetition property is:
        i ∈ C_s -> i + jm ∈ C_s* where j ∈ {0, 1, ..., l-2}.

        Parameters:
        - m: The original size of the certificate.
        
        Updates:
        - self.expanded_classes: The expanded certificate color classes.
        """
        self.expanded_classes = {f"C_{i+1}": [] for i in range(self.k)}
        
        # Apply the repetition property to each color class
        for class_label, elements in self.color_classes.items():
            for elem in elements:
                for j in range(self.l - 1): 
                    new_elem = elem + j * self.p
                    self.expanded_classes[class_label].append(new_elem)
        # Add 0 to C_1
        self.expanded_classes["C_1"].append(0)


    def run(self):
        """
        Executes the steps to construct the color classes through power residue coloring.

        Returns:
        - A dictionary of color classes with elements.
        """
        self.construct_sequence()
        self.partition_into_color_classes()
        return self.color_classes

    def run_with_expansion(self):
        """
        Executes the steps to construct the expanded certificate by enforcing repetition.

        Parameters:
        - m: The original size of the certificate.

        Returns:
        - A dictionary of expanded color classes with elements.
        """
        self.run() 

        self.expand_certificate()
        return self.expanded_classes

    def display_color_classes(self):
        """
        Displays the original color classes.
        """
        print(f"Certificate in color classes for W({self.k}, {self.l}, {self.p})")
        for class_label, elements in self.color_classes.items():
            print(f"{class_label}: {sorted(elements)}")

    def display_expanded_classes(self):
        """
        Displays the expanded color classes.
        """
        print(f"Certificate in color classes for W({self.k}, {self.l}, {self.p * (self.l - 1) + 1})")
        for class_label, elements in self.expanded_classes.items():
            print(f"{class_label}: {sorted(elements)}")


#create W(4, 3, 75)
# pr_coloring = PowerResidueColoring(p=37, k=4, l=3)
# expanded_color_classes = pr_coloring.run_with_expansion()
# pr_coloring.display_color_classes()
# pr_coloring.display_expanded_classes()
