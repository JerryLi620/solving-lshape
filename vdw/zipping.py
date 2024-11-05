from sympy import isprime, primefactors, ceiling
import math
from power_residue_coloring import PowerResidueColoring
class ZippingCertificate:
    def __init__(self, k, l, p, q_list):
        """
        Initializes the ZippingCertificate instance.

        Parameters:
        - k: The number of color classes.
        - l: The length of arithmetic progressions.
        - p: A prime number for the base certificate W(k, l, p).
        - q: A list of prime number used in the zipping method.
        """
        if not isprime(p):
            raise ValueError("p must be a prime number.")
        
        self.k = k  
        self.l = l  
        self.p = p  
        self.q_list = q_list
        self.color_classes = {}
        self.zipped_classes = {}
        self.zipped_classes_temp = {}

    def get_base_certificate(self):
        """
        Sets the base certificate W(k, l, p) with power residue coloring.
        """
        prc = PowerResidueColoring(self.p, self.k, self.l)
        self.color_classes = prc.run()
        self.zipped_classes_temp = self.color_classes
        return self.color_classes

    def zipping(self, p, q):
        """
        Performs the zipping operation to construct W(k, l, pq) from W(k, l, p).
        """
        self.zipped_classes = {f"C_{i+1}": [] for i in range(self.k)}
        for class_label, elements in self.zipped_classes_temp.items():
            s = int(class_label.split('_')[1])
            for i in elements:
                for j in range(q):
                    # Zipping
                    new_elem = (i * q + j * self.p - 1) % (p*q)+1
                    
                    new_class = (s - 1 + j * ceiling(self.k / 2)) % self.k + 1
                    self.zipped_classes[f"C_{new_class}"].append(new_elem)
        self.zipped_classes_temp = self.zipped_classes
        return self.zipped_classes

    def apply_repetition_property(self, m):
        """
        Applies the repetition property to construct W(k, l, pq(l-1) + 1).

        Parameters:
        - m: The size of the base certificate W(k, l, pq).
        
        Returns:
        - expanded_classes: The expanded certificate after applying repetition.
        """
        expanded_classes = {f"C_{i+1}": [] for i in range(self.k)}

        # Apply the repetition property
        for class_label, elements in self.zipped_classes.items():
            for elem in elements:
                for j in range(self.l - 1):
                    new_elem = elem + j * m
                    expanded_classes[class_label].append(new_elem)

        return expanded_classes

    def run(self):
        """
        Performs the full zipping and repetition process and displays the final certificate.

        This method combines zipping and repetition into a single step.

        Returns:
        - expanded_classes: The final certificate after expansion.
        """
        print(f"Generating certificate W({self.k}, {self.l}, {self.p * (math.prod(self.q_list) * (self.l - 1)) + 1})")
        base_classes = self.get_base_certificate()
        print(f"Generating W({self.k}, {self.l}, {self.p})")
        self.display_classes(base_classes)
        # Perform the zipping
        print(f"Generating W({self.k}, {self.l}, {self.p * math.prod(self.q_list)}) through zipping")
        p = self.p
        for i, q in enumerate(self.q_list):
            zipped_classes = self.zipping(p, q)
            p*=q # not mentioned in Heule's paper!!!
            if i == len(self.q_list)-1:
                self.zipped_classes["C_1"].append(0) #add 0 in the last zipping run
            self.display_classes(zipped_classes)    
        
        # Apply the repetition property
        print(f"Generating W({self.k}, {self.l}, {self.p * (math.prod(self.q_list) * (self.l - 1)) + 1})")
        expanded_classes = self.apply_repetition_property(m=self.p*math.prod(self.q_list))

        # Display the expanded color classes
        self.display_classes(expanded_classes)

        return expanded_classes

    def display_classes(self, classes):
        """
        Displays the color classes.

        Parameters:
        - classes: The dictionary of color classes to display.
        """
        for class_label, elements in classes.items():
            print(f"{class_label}: {sorted(elements)}")


zipping_cert = ZippingCertificate(k=2, l=5, p=11, q_list=[2,2])
zipping_cert.run()

